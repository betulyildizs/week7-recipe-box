# Agent B Work Log

## Task

Implement `GET /recipes?tag=<tag>` so it returns only recipes containing the
requested tag, while preserving `GET /recipes` behavior when no tag is supplied.

## Implementation

- Added an optional `tag` query parameter to the existing list endpoint.
- Kept recipe retrieval ordered and reused `_row_to_recipe` so filtering uses
  the existing JSON tag storage and response representation.
- Filtered by exact membership in each decoded tag list. This avoids substring
  matches and does not rely on SQLite JSON extensions.
- Documented the query parameter in the README.
- Added tests for matching and exact tag behavior, nonmatching and empty
  results, and listing without a tag.

## Tests

- `pytest -q` — 7 passed.
- `git diff --check` — passed.

## Risks and observations

- Tests use the application's SQLite database, which can retain recipe rows
  between runs. The filter assertions therefore verify the relevant records
  and tag membership rather than assuming a pristine database.
- Pytest reports an existing Starlette deprecation warning about using
  `httpx` with `starlette.testclient`; all tests pass.
