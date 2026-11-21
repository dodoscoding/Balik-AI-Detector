"""The corpus rules, in one place: allowed values, the date cutoff and the id format.

Builders (corpus_sources, build_corpus) and the manifest checker all import from here.
"""

import re

HUMAN_CUTOFF = "2022-11-30"

SOURCE_PERSUADE = "persuade-2.0"
SOURCE_ARXIV = "arxiv"
SOURCES = (SOURCE_PERSUADE, SOURCE_ARXIV)

PRODUCT_LICENSES = ("CC-BY-4.0", "CC-BY-3.0", "CC0-1.0", "public-domain")
INTERNAL_LICENSES = (
    "CC-BY-SA-4.0", "CC-BY-SA-3.0", "CC-BY-NC-4.0", "CC-BY-NC-SA-4.0", "CC-BY-NC-ND-4.0",
)
LICENSE_CC_BY_4 = "CC-BY-4.0"

USE_PRODUCT = "product"
USE_INTERNAL = "internal"
USES = (USE_PRODUCT, USE_INTERNAL)

HUMAN = "human"
UNKNOWN = "unknown"
AI = "ai"
MIXED = "mixed"
SOURCE_TYPES = (HUMAN, UNKNOWN, AI, MIXED)
ARCHIVE_TYPES = (HUMAN, UNKNOWN)

REGISTER_SCHOOL = "school_student"
REGISTER_ACADEMIC = "published_academic"
REGISTERS = (REGISTER_SCHOOL, "university_student", REGISTER_ACADEMIC)

LANGUAGE_EN = "en"
LANGUAGES = (LANGUAGE_EN,)

CONTEXT_ACADEMIC = "academic"
WRITING_CONTEXTS = (CONTEXT_ACADEMIC, "general")

DEV = "dev"
TEST = "test"
SPLITS = (DEV, TEST)

CODE = re.compile(r"[A-Z][A-Z0-9._-]{2,127}")


def is_code(value):
    return isinstance(value, str) and CODE.fullmatch(value) is not None
