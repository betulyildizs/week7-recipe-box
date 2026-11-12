# Starter — Recipe Box

A tiny FastAPI + SQLite service with a static frontend. Your playground for concurrent
agents and a generator–critic loop.

## Setup
```bash
python -m pip install -r requirements.txt
python -m pytest -q         # 24 tests
uvicorn main:app --reload   # http://localhost:8000 (UI at /, API docs at /docs)
```

## Endpoints
- `POST /recipes` — create a recipe with `title`, `ingredients`, and `tags`.
- `GET /recipes` — list recipes; `GET /recipes?tag=breakfast` filters by exact tag.
- `GET /recipes/{id}` — retrieve one recipe.
- `GET /shopping-list?ids=1,2` — combine ingredients in recipe order, removing
  duplicate ingredient strings.
- `GET /recipes/{id}/scaled?factor=2` — scale leading numeric ingredient
  quantities by a positive factor; non-quantity ingredients are unchanged.

## Parallel work with git worktrees
```bash
git worktree add ../recipe-task-a -b feat/shopping-list
git worktree add ../recipe-task-b -b feat/tag-filter
```

## Files
- `main.py` — the app
- `static/index.html` — minimal UI
- `test_main.py` — pytest suite
- `docs/TASKS.md` — independent tasks (safe to run in parallel)
