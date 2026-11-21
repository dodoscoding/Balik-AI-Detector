from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from corpus_split import assign_split  # noqa: E402


def rec(ident, authors, prompt):
    return {"id": ident, "authors": authors, "prompt": prompt}


class AssignSplitTests(unittest.TestCase):
    def test_shared_author_forces_same_side(self):
        records = [rec("D1", ["A-1"], "P1"), rec("D2", ["A-1"], "P2")]
        records += [rec(f"X{n}", [f"A-X{n}"], f"PX{n}") for n in range(30)]
        for seed in range(20):
            split = assign_split(records, 0.5, seed)
            self.assertEqual(split["D1"], split["D2"])

    def test_shared_prompt_forces_same_side(self):
        records = [rec("D1", ["A-1"], "P1"), rec("D2", ["A-2"], "P1")]
        records += [rec(f"X{n}", [f"A-X{n}"], f"PX{n}") for n in range(30)]
        for seed in range(20):
            split = assign_split(records, 0.5, seed)
            self.assertEqual(split["D1"], split["D2"])

    def test_chain_links_transitively(self):
        records = [rec("D1", ["A-1"], "P1"), rec("D2", ["A-1"], "P2"), rec("D3", ["A-3"], "P2")]
        records += [rec(f"X{n}", [f"A-X{n}"], f"PX{n}") for n in range(30)]
        split = assign_split(records, 0.5, 3)
        self.assertEqual(len({split["D1"], split["D2"], split["D3"]}), 1)

    def test_deterministic_and_seed_sensitive(self):
        records = [rec(f"D{n}", [f"A-{n}"], f"P{n}") for n in range(100)]
        self.assertEqual(assign_split(records, 0.2, 7), assign_split(records, 0.2, 7))
        self.assertNotEqual(assign_split(records, 0.2, 7), assign_split(records, 0.2, 8))

    def test_input_order_does_not_matter(self):
        records = [rec(f"D{n}", [f"A-{n}"], f"P{n}") for n in range(50)]
        self.assertEqual(assign_split(records, 0.2, 1), assign_split(records[::-1], 0.2, 1))

    def test_fraction_is_approximate(self):
        records = [rec(f"D{n}", [f"A-{n}"], f"P{n}") for n in range(200)]
        split = assign_split(records, 0.2, 5)
        self.assertEqual(sum(v == "test" for v in split.values()), 40)
        self.assertEqual(set(split.values()), {"dev", "test"})

    def test_every_record_gets_a_side(self):
        records = [rec(f"D{n}", [f"A-{n % 7}"], f"P{n % 3}") for n in range(40)]
        self.assertEqual(set(assign_split(records, 0.25, 1)), {r["id"] for r in records})


if __name__ == "__main__":
    unittest.main()
