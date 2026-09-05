from __future__ import annotations

import httpx
import pytest


@pytest.mark.asyncio
async def test_create_workflow(client: httpx.AsyncClient) -> None:
    response = await client.post("/workflows", json={"name": "My Workflow"})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "My Workflow"
    assert "id" in body


@pytest.mark.asyncio
async def test_latest_version_is_none_for_new_workflow(client: httpx.AsyncClient) -> None:
    create = await client.post("/workflows", json={"name": "Empty"})
    workflow_id = create.json()["id"]

    response = await client.get(f"/workflows/{workflow_id}/versions/latest")

    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.asyncio
async def test_save_and_load_round_trip(client: httpx.AsyncClient) -> None:
    create = await client.post("/workflows", json={"name": "Round Trip"})
    workflow_id = create.json()["id"]

    node_a = "11111111-1111-1111-1111-111111111111"
    node_b = "22222222-2222-2222-2222-222222222222"
    graph = {
        "nodes": [
            {"id": node_a, "type": "text_input", "position": {"x": 0, "y": 0}, "config": {}},
            {"id": node_b, "type": "output", "position": {"x": 200, "y": 0}, "config": {}},
        ],
        "edges": [
            {
                "id": "33333333-3333-3333-3333-333333333333",
                "from_node": node_a,
                "from_port": "text",
                "to_node": node_b,
                "to_port": "value",
            }
        ],
    }

    save = await client.post(f"/workflows/{workflow_id}/versions", json=graph)
    assert save.status_code == 201
    assert save.json()["version"] == 1

    load = await client.get(f"/workflows/{workflow_id}/versions/latest")
    assert load.status_code == 200
    loaded = load.json()
    assert loaded["version"] == 1
    assert len(loaded["graph"]["nodes"]) == 2
    assert len(loaded["graph"]["edges"]) == 1
    assert {n["type"] for n in loaded["graph"]["nodes"]} == {"text_input", "output"}
    assert {n["id"] for n in loaded["graph"]["nodes"]}.isdisjoint({node_a, node_b})


@pytest.mark.asyncio
async def test_second_save_creates_a_new_version(client: httpx.AsyncClient) -> None:
    create = await client.post("/workflows", json={"name": "Versioned"})
    workflow_id = create.json()["id"]
    empty_graph: dict[str, list[object]] = {"nodes": [], "edges": []}

    first = await client.post(f"/workflows/{workflow_id}/versions", json=empty_graph)
    second = await client.post(f"/workflows/{workflow_id}/versions", json=empty_graph)

    assert first.json()["version"] == 1
    assert second.json()["version"] == 2


@pytest.mark.asyncio
async def test_unknown_node_type_is_rejected_with_422(client: httpx.AsyncClient) -> None:
    create = await client.post("/workflows", json={"name": "Invalid"})
    workflow_id = create.json()["id"]

    node_a = "44444444-4444-4444-4444-444444444444"
    graph = {
        "nodes": [
            {"id": node_a, "type": "does_not_exist", "position": {"x": 0, "y": 0}, "config": {}},
        ],
        "edges": [],
    }

    response = await client.post(f"/workflows/{workflow_id}/versions", json=graph)

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "workflow_validation_failed"
    assert body["details"][0]["code"] == "unknown_node_type"


@pytest.mark.asyncio
async def test_unknown_workflow_returns_404(client: httpx.AsyncClient) -> None:
    response = await client.get(
        "/workflows/00000000-0000-0000-0000-000000000000/versions/latest"
    )

    assert response.status_code == 404
