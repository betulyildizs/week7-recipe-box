# Week 7 — Agent Orchestration: The Recipe Box Sprint

## Overview

The Recipe Box Sprint extended a small FastAPI and SQLite application through
three independent features: an ordered, de-duplicated shopping list; exact-tag
filtering for recipe listings; and ingredient quantity scaling. The first two
features were developed in parallel worktrees, and ingredient scaling was
developed and refined through a generator–critic loop.

## Part I — Concurrent Agents

Two Copilot Agent Mode sessions ran concurrently in separate VS Code windows
and Git worktrees. Agent A owned the shopping-list task on branch
`feat/shopping-list` in worktree `recipe-task-a`; Agent B independently owned
tag filtering on `feat/tag-filter` in `recipe-task-b`. The integration
workspace was `week7-recipe-box` on `main`.

Each agent had its own checkout and branch, so its edits were isolated from the
other agent and from `main` while implementation was in progress. The Git
worktree inventory confirms three separate working directories, and the commit
graph preserves the independent feature commits (`f1277db` and `45c6371`)
before their integration merges. This separation prevented either agent from
changing the integration branch prematurely; changes reached `main` only
through deliberate merges.

### Integration and Collision Management

Integration produced real merge conflicts in `README.md` and `test_main.py`.
Both branches had added endpoint documentation in the same README section and
tests near the same recipe-list test section. The resolution retained both
features and their tests: the README describes exact-tag filtering and the
ordered shopping list, while the combined test suite keeps the tag-filter
cases, shopping-list cases, and the existing unknown-recipe test. Tests use
the isolated temporary-database fixture.

`main.py` merged automatically. The resulting application contains both the
optional exact-membership tag filter and the shopping-list endpoint. The
integrated implementation was verified with the combined tests before the
ingredient-scaling work was merged.

## Part II — Generator–Critic Loop

The task was ingredient scaling at `GET /recipes/{id}/scaled?factor=...`.
The generator initially implemented quantity scaling; critic feedback led to
two revisions before final approval. The evidence sequence is:

1. **Initial generator — `1314691`:** added the ingredient-scaling endpoint,
   implementation, initial tests, and README endpoint documentation.
2. **Critic Review 1 — CHANGES REQUESTED:** identified that an extreme finite
   factor such as `1e999999` could trigger an unhandled `decimal.Overflow`.
3. **Revision 1 — `c40eb60`:** handled the extreme scaling case with a
   controlled HTTP 422 response and added a regression test.
4. **Critic Review 2 — APPROVED:** approved the revision and suggested
   automated fractional-factor tests as an optional improvement.
5. **Revision 2 — `3ff38c7`:** added parametrized cases for factors `0.5` and
   `2.25`.
6. **Final Critic — APPROVED:** Generator–Critic Loop Complete.

This is a chronological evidence log, not a verbatim conversation transcript;
it records the review outcomes and changes without inventing dialogue or
timestamps.

## Autonomy and Supervision

Each agent independently implemented its assigned feature and added tests in
its own worktree. The human supervised task assignment and isolation, reviewed
integration, resolved the documentation and test-file conflicts while
preserving both contributions, and verified the merged behavior. For scaling,
the critic independently assessed correctness and tests; its concrete
overflow finding led to a focused fix, and its optional test suggestion
prompted additional coverage before final approval. This review step provided
useful scrutiny beyond simply accepting the generator's first passing
implementation.

## Testing and Verification

The final run, `.\.venv\Scripts\python.exe -m pytest -q`, completed with **24
passed**. It reported one existing `StarletteDeprecationWarning` concerning
`httpx` with `starlette.testclient`; it did not fail the test run.

## Lessons Learned

Separate worktrees let parallel agents work independently without exposing
unfinished edits on the integration branch. Independent task ownership
reduced coordination overhead, but shared README and test sections still
created merge conflicts that required a careful combined resolution. Keeping
the feature branches and integration tests made it possible to preserve both
implementations rather than choosing one side of a conflict. The iterative
critic review also caught an extreme-input failure and improved coverage
before the scaling task was considered complete.

## Submission

From the project directory, install dependencies, run the tests, and start the
application with:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
uvicorn main:app --reload
```

The application is available at `http://localhost:8000/`; interactive API
documentation is at `http://localhost:8000/docs`.

**GitHub repository URL:** Pending publication.
