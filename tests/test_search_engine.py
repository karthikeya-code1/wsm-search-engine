import unittest
from pathlib import Path

from search_engine.document_loader import Document, load_documents
from search_engine.inverted_index import InvertedIndex
from search_engine.normalizer import normalize, normalize_tokens
from search_engine.query_processor import (
    QueryProcessor, QuerySyntaxError, difference, intersect, union)
from search_engine.tokenizer import tokenize
from search_engine.wildcard import KGramIndex

DOCS = [
    Document(1, "a.txt", "The quick brown fox."),
    Document(2, "b.txt", "A quick COMPUTER computes."),
    Document(3, "c.txt", "Brown bears don't use e-mail."),
    Document(4, "d.txt", "Compression of computing data."),
]


def make_processor():
    index = InvertedIndex.build(DOCS)
    return QueryProcessor(index, KGramIndex(index.vocabulary))


class TokenizerTests(unittest.TestCase):
    def test_splits_on_punctuation(self):
        self.assertEqual(tokenize("Hello, world! It's e-mail."),
                         ["Hello", "world", "It's", "e-mail"])


class NormalizerTests(unittest.TestCase):
    def test_case_folding(self):
        self.assertEqual(normalize("COMPUTER"), "computer")

    def test_strips_apostrophes_and_hyphens(self):
        self.assertEqual(normalize_tokens(["don't", "e-mail", "-"]), ["dont", "email"])


class IndexTests(unittest.TestCase):
    def test_postings(self):
        index = InvertedIndex.build(DOCS)
        self.assertEqual(index.postings("quick"), [1, 2])
        self.assertEqual(index.postings("brown"), [1, 3])
        self.assertEqual(index.postings("missing"), [])


class MergeTests(unittest.TestCase):
    def test_merges(self):
        self.assertEqual(intersect([1, 3, 5], [3, 4, 5]), [3, 5])
        self.assertEqual(union([1, 3], [2, 3, 6]), [1, 2, 3, 6])
        self.assertEqual(difference([1, 2, 3, 4], [2, 4]), [1, 3])


class QueryTests(unittest.TestCase):
    def setUp(self):
        self.qp = make_processor()

    def ids(self, q):
        return self.qp.search(q).doc_ids

    def test_single_term_is_case_insensitive(self):
        self.assertEqual(self.ids("QUICK"), [1, 2])

    def test_and_or_not(self):
        self.assertEqual(self.ids("quick AND brown"), [1])
        self.assertEqual(self.ids("quick brown"), [1])          # implicit AND
        self.assertEqual(self.ids("quick OR bears"), [1, 2, 3])
        self.assertEqual(self.ids("NOT quick"), [3, 4])
        self.assertEqual(self.ids("brown and not fox"), [3])

    def test_precedence_and_parentheses(self):
        self.assertEqual(self.ids("fox OR quick AND computer"), [1, 2])
        self.assertEqual(self.ids("(fox OR quick) AND computer"), [2])

    def test_normalized_query_terms(self):
        self.assertEqual(self.ids("email"), [3])
        self.assertEqual(self.ids("DON'T"), [3])

    def test_syntax_errors(self):
        for bad in ["quick AND", "(quick", "quick )", "OR fox"]:
            with self.assertRaises(QuerySyntaxError, msg=bad):
                self.qp.search(bad)


class WildcardTests(unittest.TestCase):
    def setUp(self):
        self.kg = make_processor().kgram_index

    def test_prefix_suffix_infix(self):
        self.assertEqual(self.kg.expand("comp*"),
                         ["compression", "computer", "computes", "computing"])
        self.assertEqual(self.kg.expand("*ing"), ["computing"])
        self.assertEqual(self.kg.expand("comp*r"), ["computer"])
        self.assertEqual(self.kg.expand("*ow*"), ["brown"])

    def test_post_filter_removes_false_positives(self):
        # "co*on" shares bigrams $c, co, on, n$ with "compression" only;
        # it must also really match the pattern.
        self.assertEqual(self.kg.expand("co*on"), ["compression"])
        self.assertEqual(self.kg.expand("q*n"), [])

    def test_short_pieces_and_case(self):
        self.assertEqual(self.kg.expand("F*"), ["fox"])

    def test_wildcard_in_query(self):
        qp = make_processor()
        result = qp.search("comp* AND NOT quick")
        self.assertEqual(result.doc_ids, [4])
        self.assertIn("comp*", result.expansions)


class LoaderTests(unittest.TestCase):
    def test_loads_sample_data(self):
        docs = load_documents(Path(__file__).parent.parent / "data")
        self.assertGreater(len(docs), 0)
        self.assertEqual([d.doc_id for d in docs], list(range(1, len(docs) + 1)))


if __name__ == "__main__":
    unittest.main()
