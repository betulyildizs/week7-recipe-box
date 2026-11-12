# Agent A Work Log

## Task

Implemented Task 1 from `docs/TASKS.md`: `GET /shopping-list?ids=1,2,3` combines
ingredients from the requested recipes into a de-duplicated list.

## Implementation decisions

- Returns a JSON array of ingredient strings, preserving the order recipes and
  ingredients are first encountered.
- Removes duplicate recipe IDs before fetching and duplicate ingredient strings
  while constructing the result.
- Accepts surrounding whitespace around numeric IDs, but rejects empty segments,
  non-integers, and zero or negative IDs with HTTP 422.
- Returns HTTP 404 with the existing `unknown recipe` detail if any requested
  recipe does not exist.
- Uses parameterized SQLite values and the existing JSON ingredient storage.
- Updated the README endpoint list and isolated each pytest case in a temporary
  SQLite database.

## Tests run

- Baseline before changes: `pytest -q` — 3 passed.
- After implementation: `pytest -q` — 12 passed.

The test run emitted one existing Starlette deprecation warning about
`httpx` in `TestClient`.

## Risks

Ingredient de-duplication uses exact string equality and preserves the first
occurrence; differently cased or formatted strings remain separate. No other
risks were encountered during implementation or validation.
