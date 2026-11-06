"""A small Boolean information-retrieval engine with wildcard support.

Pipeline:
    document_loader -> tokenizer -> normalizer -> inverted_index
    query_processor (+ wildcard) -> gui
"""
