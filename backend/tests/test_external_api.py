import pytest

def test_perplexity_unavailable(monkeypatch, client):
    async def broken_call(prompt, domain_filter=None):
        raise ConnectionError("Perplexity unreachable")
    monkeypatch.setattr("app.ai.perplexity_api.call_perplexity", broken_call)

    payload = {"route_request": "Ошибка", "minutes": 30, "language": "ru", "start_point": None, "selected_categories": []}
    resp = client.post("/api/route/generate", json=payload)
    # Service should return 500 or a 4xx with error message; accept 500/503/400
    assert resp.status_code in (500, 503, 400)
    j = resp.json()
    assert "detail" in j or "error" in j
