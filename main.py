"""Entry point: load documents, build indexes, launch the GUI.

Usage:
    python main.py              # uses ./data
    python main.py path/to/docs
"""

import sys
from pathlib import Path

from search_engine.document_loader import load_documents
from search_engine.gui import run_gui
from search_engine.inverted_index import InvertedIndex
from search_engine.query_processor import QueryProcessor
from search_engine.wildcard import KGramIndex


def main() -> None:
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "data"
    documents = load_documents(folder)
    index = InvertedIndex.build(documents)
    processor = QueryProcessor(index, KGramIndex(index.vocabulary))
    run_gui(processor)


if __name__ == "__main__":
    main()
