import json
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import corpus_rules  # noqa: E402
import corpus_sources as cs  # noqa: E402


def persuade_row(**overrides):
    row = {
        "essay_id_comp": "423A1CA112E2",
        "competition_set": "train",
        "full_text": "Phones should be allowed.\nThey help students.",
        "prompt_name": "Phones and driving",
        "grade_level": "10",
    }
    row.update(overrides)
    return row


class PersuadeTests(unittest.TestCase):
    def test_competition_essay_is_human_dated_by_publication(self):
        fields, text = cs.persuade_document(persuade_row(), published_by="2022-03-25")
        self.assertEqual(text, "Phones should be allowed.\nThey help students.")
        self.assertEqual(fields["id"], "PERSUADE-423A1CA112E2")
        self.assertEqual(fields["source"], "persuade-2.0")
        self.assertEqual(fields["source_ref"], "423A1CA112E2")
        self.assertEqual(fields["license"], "CC-BY-4.0")
        self.assertEqual(fields["use"], "product")
        self.assertEqual(fields["date"], "2022-03-25")
        self.assertEqual(fields["source_type"], "human")
        self.assertEqual(fields["register"], "school_student")
        self.assertIn("grades 6", fields["population"])
        self.assertEqual(fields["authors"], ["STUDENT-423A1CA112E2"])
        self.assertEqual(fields["prompt"], "PROMPT-PHONES-AND-DRIVING")
        self.assertIsNone(fields["derived_from"])

    def test_essay_without_competition_id_is_left_out(self):
        row = persuade_row(essay_id_comp="", competition_set="")
        self.assertIsNone(cs.persuade_document(row, published_by="2022-03-25"))

    def test_blank_text_is_skipped(self):
        self.assertIsNone(cs.persuade_document(persuade_row(full_text="  "), published_by="2022-03-25"))


class LicenseTests(unittest.TestCase):
    def test_normalize(self):
        cases = {
            "http://creativecommons.org/licenses/by/4.0/": "CC-BY-4.0",
            "https://creativecommons.org/licenses/by/3.0/": "CC-BY-3.0",
            "http://creativecommons.org/publicdomain/zero/1.0/": "CC0-1.0",
            "Public Domain": "public-domain",
            "Creative Commons - Attribution - https://creativecommons.org/licenses/by/4.0/": "CC-BY-4.0",
            "Creative Commons - Attribution Share-Alike - https://creativecommons.org/licenses/by-sa/4.0/": "CC-BY-SA-4.0",
            "http://arxiv.org/licenses/nonexclusive-distrib/1.0/": None,
            "": None,
            None: None,
        }
        for raw, expected in cases.items():
            self.assertEqual(cs.normalize_license(raw), expected, raw)


class RulesTests(unittest.TestCase):
    def test_every_license_pattern_emits_a_code_the_rules_know(self):
        known = set(corpus_rules.PRODUCT_LICENSES) | set(corpus_rules.INTERNAL_LICENSES)
        for code, _ in cs.LICENSE_PATTERNS:
            self.assertIn(code, known)

    def test_pes2o_is_not_a_source(self):
        self.assertNotIn("pes2o", corpus_rules.SOURCES)


def pile_record(**overrides):
    intro = "\n\n".join(f"Paragraph {n} " + "word " * 100 for n in range(5))
    text = (
        "# A Title\n\nAuthor Name\n\n###### Abstract\n\nShort abstract.\n\n"
        f"##  1 Introduction\n\n{intro}\n\n##  2 Methods\n\nMethods text."
    )
    record = {
        "id": "0705.1023",
        "text": text,
        "created": "2007-05-08T01:01:59",
        "metadata": {
            "license": "Creative Commons - Attribution - https://creativecommons.org/licenses/by/4.0/",
            "authors": "Ana Álvarez, B. Smith, and Chen Li",
        },
    }
    record.update(overrides)
    return record


class IntroductionTests(unittest.TestCase):
    def test_extracts_section_after_abstract_up_to_next_heading(self):
        intro = cs.extract_introduction(pile_record()["text"])
        self.assertTrue(intro.startswith("Paragraph 0"))
        self.assertNotIn("Methods", intro)
        self.assertNotIn("Short abstract", intro)

    def test_trims_at_paragraph_boundary(self):
        paragraphs = ["w " * 500] * 4
        text = "## 1. Introduction\n\n" + "\n\n".join(paragraphs) + "\n\n## 2. Next\n\nx"
        intro = cs.extract_introduction(text)
        self.assertEqual(len(intro.split()), 1000)
        self.assertEqual(intro.count("\n\n"), 1)

    def test_too_short_or_missing_returns_none(self):
        self.assertIsNone(cs.extract_introduction("## 1 Introduction\n\nshort.\n\n## 2 X\n\ny"))
        self.assertIsNone(cs.extract_introduction("# Title\n\nno sections here"))

    def test_first_paragraph_longer_than_limit_returns_none(self):
        text = "## Introduction\n\n" + "w " * 1500 + "\n\n## Next\n\nx"
        self.assertIsNone(cs.extract_introduction(text))

    def test_math_heavy_introduction_is_rejected(self):
        text = "## Introduction\n\n" + "$x$ " * 400 + "\n\n## Next\n\nx"
        self.assertIsNone(cs.extract_introduction(text))


class CommonPileTests(unittest.TestCase):
    def test_record_becomes_candidate(self):
        candidate = cs.common_pile_candidate(pile_record())
        self.assertEqual(candidate["arxiv_id"], "0705.1023")
        self.assertEqual(candidate["license"], "CC-BY-4.0")
        self.assertEqual(len(candidate["authors"]), 3)
        self.assertTrue(all(a.startswith("A-") and len(a) == 14 for a in candidate["authors"]))
        self.assertTrue(candidate["text"].startswith("Paragraph 0"))

    def test_share_alike_and_missing_intro_are_dropped(self):
        sa = pile_record()
        sa["metadata"]["license"] = "Creative Commons - Attribution Share-Alike - https://creativecommons.org/licenses/by-sa/4.0/"
        self.assertIsNone(cs.common_pile_candidate(sa))
        self.assertIsNone(cs.common_pile_candidate(pile_record(text="# T\n\nnothing")))

    def test_author_code_ignores_case_accents_and_spacing(self):
        self.assertEqual(cs.author_code("Ana  Álvarez"), cs.author_code("ana alvarez"))
        self.assertNotEqual(cs.author_code("Ana Alvarez"), cs.author_code("Ana Alvarz"))

    def test_authors_split_on_commas_and_and(self):
        self.assertEqual(
            cs.split_authors("A One, B Two, and C Three"), ["A One", "B Two", "C Three"]
        )
        self.assertEqual(cs.split_authors("A One and B Two"), ["A One", "B Two"])


OAI = """<?xml version="1.0"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"><GetRecord><record><metadata>
<arXiv xmlns="http://arxiv.org/OAI/arXiv/"><id>0705.1023</id><created>2007-05-08</created>
{updated}<license>http://creativecommons.org/licenses/by/4.0/</license></arXiv>
</metadata></record></GetRecord></OAI-PMH>"""


class OaiTests(unittest.TestCase):
    def test_parses_license_and_dates(self):
        xml = OAI.format(updated="<updated>2009-01-02</updated>")
        self.assertEqual(
            cs.parse_oai(xml), ("http://creativecommons.org/licenses/by/4.0/", "2007-05-08", "2009-01-02")
        )

    def test_missing_updated_is_none(self):
        self.assertEqual(cs.parse_oai(OAI.format(updated=""))[2], None)

    def test_error_response_returns_none(self):
        self.assertIsNone(cs.parse_oai('<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/"><error code="idDoesNotExist"/></OAI-PMH>'))

    def test_verified_date_and_license(self):
        ok = cs.verify_oai(("http://creativecommons.org/licenses/by/4.0/", "2007-05-08", "2009-01-02"))
        self.assertEqual(ok, ("CC-BY-4.0", "2009-01-02"))
        self.assertEqual(cs.verify_oai(("http://creativecommons.org/licenses/by/4.0/", "2007-05-08", None)), ("CC-BY-4.0", "2007-05-08"))

    def test_rejections(self):
        self.assertIsNone(cs.verify_oai(("http://arxiv.org/licenses/nonexclusive-distrib/1.0/", "2007-05-08", None)))
        self.assertIsNone(cs.verify_oai(("http://creativecommons.org/licenses/by-sa/4.0/", "2007-05-08", None)))
        self.assertIsNone(cs.verify_oai(("http://creativecommons.org/licenses/by/4.0/", "2007-05-08", "2022-11-30")))
        self.assertIsNone(cs.verify_oai(None))

    def test_arxiv_document_fields(self):
        candidate = cs.common_pile_candidate(pile_record())
        fields, text = cs.arxiv_document(candidate, "CC-BY-3.0", "2009-01-02")
        self.assertEqual(fields["id"], "ARXIV-0705.1023")
        self.assertEqual(fields["license"], "CC-BY-3.0")
        self.assertEqual(fields["use"], "product")
        self.assertEqual(fields["date"], "2009-01-02")
        self.assertEqual(fields["source_type"], "human")
        self.assertEqual(fields["register"], "published_academic")
        self.assertEqual(fields["prompt"], "ARXIV-0705.1023")

    def test_old_style_ids_become_codes(self):
        self.assertEqual(cs.arxiv_code("hep-th/9901001"), "ARXIV-HEP-TH_9901001")


if __name__ == "__main__":
    unittest.main()
