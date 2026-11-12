import pytest
from fastapi.testclient import TestClient

import main
from main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "recipes.db")
    main.init_db()
    with TestClient(app) as test_client:
        yield test_client


def test_create_and_get_recipe(client):
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


def test_list_recipes(client):
    client.post("/recipes", json={"title": "Toast"})
    r = client.get("/recipes")
    assert r.status_code == 200
    assert any(rec["title"] == "Toast" for rec in r.json())


def test_unknown_recipe_404(client):
    r = client.get("/recipes/99999")
    assert r.status_code == 404


def test_scaled_recipe_multiplies_quantities_and_preserves_other_fields(client):
    recipe = client.post(
        "/recipes",
        json={
            "title": "Pancakes",
            "ingredients": ["200 g flour", "1.5 cups milk", "salt to taste"],
            "tags": ["breakfast"],
        },
    ).json()

    response = client.get(f"/recipes/{recipe['id']}/scaled", params={"factor": "2"})

    assert response.status_code == 200
    assert response.json() == {
        **recipe,
        "ingredients": ["400 g flour", "3 cups milk", "salt to taste"],
    }


def test_scaled_recipe_returns_404_for_unknown_recipe(client):
    response = client.get("/recipes/99999/scaled", params={"factor": "2"})

    assert response.status_code == 404
    assert response.json() == {"detail": "unknown recipe"}


def test_scaled_recipe_rejects_factor_that_overflows_decimal(client):
    recipe_id = client.post(
        "/recipes",
        json={"title": "Bread", "ingredients": ["200 g flour"]},
    ).json()["id"]

    response = client.get(
        f"/recipes/{recipe_id}/scaled",
        params={"factor": "1e999999"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "scaled ingredient quantity is too large"
    }


@pytest.mark.parametrize("factor", ["0", "-1", "Infinity"])
def test_scaled_recipe_rejects_nonpositive_or_nonfinite_factor(client, factor):
    recipe_id = client.post("/recipes", json={"title": "Bread"}).json()["id"]

    response = client.get(
        f"/recipes/{recipe_id}/scaled",
        params={"factor": factor},
    )

    assert response.status_code == 422


def test_list_recipes_filters_by_exact_tag(client):
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


def test_list_recipes_with_nonmatching_tag_returns_empty_list(client):
    client.post("/recipes", json={"title": "Breakfast", "tags": ["breakfast"]})

    r = client.get("/recipes", params={"tag": "not-a-tag"})

    assert r.status_code == 200
    assert r.json() == []


def test_list_recipes_with_tag_returns_empty_list_when_no_recipes_match(client):
    r = client.get("/recipes", params={"tag": "unique-no-match-tag-7f4a"})

    assert r.status_code == 200
    assert r.json() == []


def test_list_recipes_without_tag_preserves_all_recipes(client):
    client.post("/recipes", json={"title": "Breakfast", "tags": ["breakfast"]})
    client.post("/recipes", json={"title": "Dinner", "tags": ["dinner"]})

    r = client.get("/recipes")

    assert r.status_code == 200
    titles = [recipe["title"] for recipe in r.json()]
    assert "Breakfast" in titles
    assert "Dinner" in titles


def test_shopping_list_merges_and_deduplicates_ingredients(client):
    first = client.post(
        "/recipes",
        json={"title": "Pancakes", "ingredients": ["flour", "milk", "flour"]},
    ).json()["id"]
    second = client.post(
        "/recipes",
        json={"title": "Bread", "ingredients": ["flour", "yeast", "water"]},
    ).json()["id"]

    response = client.get(f"/shopping-list?ids={first}, {second},{first}")

    assert response.status_code == 200
    assert response.json() == ["flour", "milk", "yeast", "water"]


def test_shopping_list_returns_404_for_missing_recipe(client):
    existing = client.post(
        "/recipes",
        json={"title": "Soup", "ingredients": ["water"]},
    ).json()["id"]

    response = client.get(f"/shopping-list?ids={existing},99999")

    assert response.status_code == 404
    assert response.json() == {"detail": "unknown recipe"}


@pytest.mark.parametrize("ids", ["", "1,,2", "one", "0", "-1", "1.5"])
def test_shopping_list_rejects_malformed_ids(client, ids):
    response = client.get("/shopping-list", params={"ids": ids})

    assert response.status_code == 422
    assert response.json() == {
        "detail": "ids must be a comma-separated list of positive integers"
    }


def test_shopping_list_requires_ids_parameter(client):
    response = client.get("/shopping-list")

    assert response.status_code == 422
