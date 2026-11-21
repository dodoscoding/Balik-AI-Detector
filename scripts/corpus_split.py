"""Assign whole author/prompt-connected groups of documents to dev or test."""

import random


def assign_split(records, test_fraction, seed):
    """Return {id: "dev" | "test"}.

    Documents that share an author code or a prompt code, directly or through a
    chain, always land on the same side. Whole groups move to test, in an order
    fixed by the seed, until the test side first reaches test_fraction of all
    documents.
    """
    parent = {}

    def find(node):
        parent.setdefault(node, node)
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def union(a, b):
        parent[find(a)] = find(b)

    for record in records:
        node = ("doc", record["id"])
        find(node)
        union(node, ("prompt", record["prompt"]))
        for author in record["authors"]:
            union(node, ("author", author))

    groups = {}
    for record in records:
        groups.setdefault(find(("doc", record["id"])), []).append(record["id"])
    ordered = sorted((sorted(ids) for ids in groups.values()), key=lambda ids: ids[0])
    random.Random(seed).shuffle(ordered)

    target = test_fraction * len(records)
    split = {}
    in_test = 0
    for ids in ordered:
        side = "test" if in_test < target else "dev"
        for ident in ids:
            split[ident] = side
        if side == "test":
            in_test += len(ids)
    return split
