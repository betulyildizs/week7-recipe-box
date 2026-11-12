from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_create_and_get_recipe():
    r = client.post(
        "/recipes",
        json={"title": "Pancakes", "ingredients": ["flour", "milk"], "tags": ["breakfast"]},
    )
    assert r.status_code == 200
    rid = r.json()["id"]
    r2 = client.get(f"/recipes/{rid}")
    assert r2.status_code == 200
    assert r2.json()["title"] == "Pancakes"
    assert r2.json()["tags"] == ["breakfast"]


def test_list_recipes():
    client.post("/recipes", json={"title": "Toast"})
    r = client.get("/recipes")
    assert r.status_code == 200
    assert any(rec["title"] == "Toast" for rec in r.json())


def test_list_recipes_filters_by_exact_tag():
    client.post("/recipes", json={"title": "Breakfast", "tags": ["breakfast"]})
    client.post("/recipes", json={"title": "Brunch", "tags": ["breakfast", "brunch"]})
    client.post("/recipes", json={"title": "Dinner", "tags": ["notbreakfast"]})

    r = client.get("/recipes", params={"tag": "breakfast"})

    assert r.status_code == 200
    titles = [recipe["title"] for recipe in r.json()]
    assert "Breakfast" in titles
    assert "Brunch" in titles
    assert "Dinner" not in titles
    assert all("breakfast" in recipe["tags"] for recipe in r.json())


def test_list_recipes_with_nonmatching_tag_returns_empty_list():
    client.post("/recipes", json={"title": "Breakfast", "tags": ["breakfast"]})

    r = client.get("/recipes", params={"tag": "not-a-tag"})

    assert r.status_code == 200
    assert r.json() == []


def test_list_recipes_with_tag_returns_empty_list_when_no_recipes_match():
    r = client.get("/recipes", params={"tag": "unique-no-match-tag-7f4a"})

    assert r.status_code == 200
    assert r.json() == []


def test_list_recipes_without_tag_preserves_all_recipes():
    client.post("/recipes", json={"title": "Breakfast", "tags": ["breakfast"]})
    client.post("/recipes", json={"title": "Dinner", "tags": ["dinner"]})

    r = client.get("/recipes")

    assert r.status_code == 200
    titles = [recipe["title"] for recipe in r.json()]
    assert "Breakfast" in titles
    assert "Dinner" in titles


def test_unknown_recipe_404():
    r = client.get("/recipes/99999")
    assert r.status_code == 404
