"""Pure parsers that turn raw archive records into manifest fields and text.

Nothing here touches the network or the disk. Raw input is untrusted data: it
is only parsed, never executed.
"""

import hashlib
import re
import unicodedata
import xml.etree.ElementTree as ET

from corpus_rules import (
    CONTEXT_ACADEMIC, HUMAN, HUMAN_CUTOFF, LANGUAGE_EN, LICENSE_CC_BY_4,
    PRODUCT_LICENSES, REGISTER_ACADEMIC, REGISTER_SCHOOL, SOURCE_ARXIV, SOURCE_PERSUADE, UNKNOWN,
    USE_PRODUCT,
)

MIN_WORDS = 300
MAX_WORDS = 1200
MAX_MATH_PER_WORD = 0.03

LICENSE_PATTERNS = (
    ("CC-BY-SA-4.0", re.compile(r"licenses/by-sa/4\.0")),
    ("CC-BY-SA-3.0", re.compile(r"licenses/by-sa/3\.0")),
    ("CC-BY-NC-SA-4.0", re.compile(r"licenses/by-nc-sa/4\.0")),
    ("CC-BY-NC-4.0", re.compile(r"licenses/by-nc/4\.0")),
    ("CC-BY-NC-ND-4.0", re.compile(r"licenses/by-nc-nd/4\.0")),
    ("CC-BY-4.0", re.compile(r"licenses/by/4\.0")),
    ("CC-BY-3.0", re.compile(r"licenses/by/3\.0")),
    ("CC0-1.0", re.compile(r"publicdomain/zero/1\.0")),
    ("public-domain", re.compile(r"^\s*public domain\s*$", re.IGNORECASE)),
)


def normalize_license(raw):
    """Map a license URL or label to a manifest license code, else None."""
    if not isinstance(raw, str):
        return None
    for code, pattern in LICENSE_PATTERNS:
        if pattern.search(raw):
            return code
    return None


def _slug(value):
    return re.sub(r"[^A-Z0-9]+", "-", value.upper()).strip("-")


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def persuade_document(row, published_by):
    """Return (manifest fields, text) for one PERSUADE 2.0 essay row, or None.

    Every row of the train CSV carries a Kaggle Feedback Prize essay id, so the
    essay was public by `published_by`. A row without that id has no date proof
    and no stable id; it is left out.
    """
    essay = (row.get("essay_id_comp") or "").strip()
    text = (row.get("full_text") or "").strip()
    prompt = _slug(row.get("prompt_name") or "")
    if not essay or not text or not prompt:
        return None
    code = _slug(essay)
    fields = {
        "id": f"PERSUADE-{code}",
        "source": SOURCE_PERSUADE,
        "source_ref": essay,
        "license": LICENSE_CC_BY_4,
        "use": USE_PRODUCT,
        "date": published_by,
        "source_type": HUMAN if published_by < HUMAN_CUTOFF else UNKNOWN,
        "register": REGISTER_SCHOOL,
        "population": "US students, grades 6-12",
        "language": LANGUAGE_EN,
        "writing_context": CONTEXT_ACADEMIC,
        "authors": [f"STUDENT-{code}"],
        "prompt": f"PROMPT-{prompt}",
        "derived_from": None,
    }
    return fields, text


def split_authors(raw):
    if not isinstance(raw, str):
        return []
    parts = re.split(r",\s*(?:and\s+)?|\s+and\s+", raw)
    return [part.strip() for part in parts if part.strip()]


def author_code(name):
    """Stable code for a normalized author name, shared across papers."""
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_name = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    normalized = " ".join(ascii_name.lower().split())
    return "A-" + hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:12].upper()


def arxiv_code(arxiv_id):
    return "ARXIV-" + re.sub(r"[^A-Z0-9._-]+", "_", arxiv_id.upper())


HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
INTRO_TITLE = re.compile(r"^[\s\d.IVX\\]*introduction\b", re.IGNORECASE)


def extract_introduction(text):
    """Return the paper's introduction trimmed to whole paragraphs, or None."""
    lines = text.split("\n")
    start = level = None
    for number, line in enumerate(lines):
        match = HEADING.match(line)
        if match and INTRO_TITLE.match(match.group(2)):
            start, level = number + 1, len(match.group(1))
            break
    if start is None:
        return None
    body = []
    for line in lines[start:]:
        match = HEADING.match(line)
        if match:
            if len(match.group(1)) <= level:
                break
            continue
        body.append(line)
    paragraphs = [" ".join(p.split()) for p in "\n".join(body).split("\n\n")]
    kept, words = [], 0
    for paragraph in paragraphs:
        if not paragraph:
            continue
        count = len(paragraph.split())
        if words + count > MAX_WORDS:
            break
        kept.append(paragraph)
        words += count
    if words < MIN_WORDS:
        return None
    intro = "\n\n".join(kept)
    if intro.count("$") / words > MAX_MATH_PER_WORD:
        return None
    return intro


def common_pile_candidate(record):
    """Return an unverified arXiv candidate from a Common Pile record, or None."""
    metadata = record.get("metadata") or {}
    license_code = normalize_license(metadata.get("license"))
    if license_code not in PRODUCT_LICENSES:
        return None
    intro = extract_introduction(record.get("text") or "")
    names = split_authors(metadata.get("authors"))
    if intro is None or not names or not record.get("id"):
        return None
    return {
        "arxiv_id": record["id"],
        "license": license_code,
        "authors": sorted({author_code(name) for name in names}),
        "text": intro,
    }


def parse_oai(xml_text):
    """Return (license, created, updated) from an OAI-PMH arXiv record, or None."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None
    node = root.find(".//{http://arxiv.org/OAI/arXiv/}arXiv")
    if node is None:
        return None

    def get(tag):
        child = node.find("{http://arxiv.org/OAI/arXiv/}" + tag)
        return child.text.strip() if child is not None and child.text else None

    return get("license"), get("created"), get("updated")


def verify_oai(parsed):
    """Return (license code, date) if arXiv confirms a product license and an early date."""
    if parsed is None:
        return None
    license_url, created, updated = parsed
    license_code = normalize_license(license_url)
    date = updated or created
    if license_code not in PRODUCT_LICENSES or not date or date >= HUMAN_CUTOFF:
        return None
    return license_code, date


def arxiv_document(candidate, license_code, date):
    code = arxiv_code(candidate["arxiv_id"])
    fields = {
        "id": code,
        "source": SOURCE_ARXIV,
        "source_ref": candidate["arxiv_id"],
        "license": license_code,
        "use": USE_PRODUCT,
        "date": date,
        "source_type": HUMAN,
        "register": REGISTER_ACADEMIC,
        "population": "Published researchers (arXiv)",
        "language": LANGUAGE_EN,
        "writing_context": CONTEXT_ACADEMIC,
        "authors": list(candidate["authors"]),
        "prompt": code,
        "derived_from": None,
    }
    return fields, candidate["text"]
