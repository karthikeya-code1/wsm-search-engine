# WSM Search Engine

A Boolean search engine with wildcard queries and a Tkinter GUI. It uses only the Python standard library (Python 3.10+).

![Search window showing a wildcard query](project_screenshots/04_wildcard.png)

## Screenshots

| | |
|:---:|:---:|
| ![AND query](project_screenshots/01_boolean_and.png) | ![NOT query](project_screenshots/02_and_not.png) |
| **AND:** `computer AND network` | **NOT:** `carbon AND NOT climate` |
| ![Grouping with parentheses](project_screenshots/03_parentheses.png) | ![Trailing wildcard](project_screenshots/04_wildcard.png) |
| **Grouping:** `(cricket OR football) AND world` | **Trailing wildcard:** `comp* AND history` |
| ![Leading wildcard](project_screenshots/05_wildcard_leading.png) | ![Error message](project_screenshots/06_error.png) |
| **Leading wildcard:** `*tion AND search` | **Error message:** `computer AND` |

## Run

```
python main.py              # indexes the .txt files in ./data
python main.py path\to\docs # or any other folder
python -m unittest -v       # tests
```

## Structure

```
main.py                       entry point: load -> index -> GUI
search_engine/
  document_loader.py   (1)    reads .txt files, assigns doc IDs
  tokenizer.py         (2)    splits text into word tokens
  normalizer.py        (3)    case folding, strips ' and -
  inverted_index.py    (4)    term -> sorted postings list
  query_processor.py   (5)    AND / OR / NOT / ( ) parser, postings merges
  wildcard.py          (6)    k-gram index, expands patterns like comp*
  gui.py               (7)    search box, Search button, read-only results
data/                         sample documents
tests/                        unit tests
```

## Query syntax

| Example                         | Meaning                              |
|---------------------------------|--------------------------------------|
| `index retrieval`               | both words (implicit AND)            |
| `boolean OR wildcard`           | either word                          |
| `retrieval AND NOT boolean`     | first word but not the second        |
| `(web OR boolean) AND retrieval`| grouping                             |
| `comp*`, `*tion`, `re*ve`       | wildcard: `*` = any characters       |

Precedence runs NOT, then AND, then OR. Operators can be written in any case.

## Wildcard method

Each vocabulary term is padded as `$term$` and split into bigrams. To answer a pattern, the engine intersects the term sets for the pattern's bigrams. It then checks each candidate against the full pattern to drop false positives. The matching terms are ORed together in the query.
