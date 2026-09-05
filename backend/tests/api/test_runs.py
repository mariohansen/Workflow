from __future__ import annotations

import httpx
import pytest


async def _create_workflow_with_graph(client: httpx.AsyncClient, name: str) -> str:
    create = await client.post("/workflows", json={"name": name})
    workflow_id = create.json()["id"]

    node_a = "11111111-1111-1111-1111-111111111111"
    node_b = "22222222-2222-2222-2222-222222222222"
    graph = {
        "nodes": [
            {
                "id": node_a,
                "type": "text_input",
                "position": {"x": 0, "y": 0},
                "config": {"value": "hello world"},
            },
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
    await client.post(f"/workflows/{workflow_id}/versions", json=graph)
    return str(workflow_id)


@pytest.mark.asyncio
async def test_node_types_endpoint_lists_registered_types(client: httpx.AsyncClient) -> None:
    response = await client.get("/node-types")

    assert response.status_code == 200
    types = {nt["type"] for nt in response.json()}
    assert types == {"text_input", "output"}


@pytest.mark.asyncio
async def test_start_run_completes_a_simple_graph(client: httpx.AsyncClient) -> None:
    workflow_id = await _create_workflow_with_graph(client, "Runnable")

    response = await client.post(f"/workflows/{workflow_id}/runs")

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "completed"
    assert len(body["steps"]) == 2
    assert {s["status"] for s in body["steps"]} == {"completed"}


@pytest.mark.asyncio
async def test_get_run_returns_the_same_status(client: httpx.AsyncClient) -> None:
    workflow_id = await _create_workflow_with_graph(client, "Queryable")
    start = await client.post(f"/workflows/{workflow_id}/runs")
    run_id = start.json()["id"]

    response = await client.get(f"/runs/{run_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_start_run_without_saved_version_returns_422(client: httpx.AsyncClient) -> None:
    create = await client.post("/workflows", json={"name": "No Version"})
    workflow_id = create.json()["id"]

    response = await client.post(f"/workflows/{workflow_id}/runs")

    assert response.status_code == 422
    assert response.json()["code"] == "no_workflow_version"


@pytest.mark.asyncio
async def test_get_unknown_run_returns_404(client: httpx.AsyncClient) -> None:
    response = await client.get("/runs/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json()["code"] == "run_not_found"
