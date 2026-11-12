# Integration Log

## Merge conflicts

- `README.md`: Both branches added endpoint documentation in the same section.
  The resolved list documents recipe listing with exact-tag filtering and the
  recipe detail endpoint, as well as the ordered, de-duplicated shopping-list
  endpoint.
- `test_main.py`: Both branches edited the section after the recipe-list test.
  The resolved suite retains the unknown-recipe test, all tag-filter tests, and
  all shopping-list tests. The tag-filter tests were updated to accept the
  existing `client` fixture so they run against isolated temporary databases.
  The unknown-recipe test appears once and also uses that fixture.

## Auto-merged implementation

`main.py` retains the tag-filter query parameter and exact membership filter
in `list_recipes`, while preserving the ordered unfiltered response when no tag
is supplied. The shopping-list endpoint remains present and keeps its
ordered/deduplicated ingredient behavior and input validation.

## Verification

- `.\.venv\Scripts\python.exe -m pytest -q` — 16 passed, 1 warning.
- The warning is Starlette's deprecation warning about using `httpx` with
  `starlette.testclient`.
- `git diff --check` — passed.
