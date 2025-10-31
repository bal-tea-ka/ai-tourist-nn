import json
import pytest

@pytest.mark.asyncio
async def test_generate_route_ai(monkeypatch, client):
    """
    Patch the call_perplexity function to return a predictable JSON string that parsers expect.
    """
    async def fake_call_perplexity(prompt, domain_filter=None):
        # Return JSON list of places as string
        return json.dumps([
            {"title": "Кремль", "address": "Кремль, Нижний Новгород", "category": {"id":1, "title":"История"}, "visit_duration": 45, "notes": "Красиво"},
            {"title": "Набережная", "address": "Волга", "category": {"id":2, "title":"Природа"}, "visit_duration": 30, "notes": ""}
        ])

    monkeypatch.setattr("app.ai.perplexity_api.call_perplexity", fake_call_perplexity)

    payload = {"route_request": "Прогулка по центру", "minutes": 120, "language": "ru", "start_point": None, "selected_categories": []}
    resp = client.post("/api/route/generate", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # The route builder returns a field "metadata" or "places" or "route" depending on implementation
    assert ("places" in data) or ("route" in data) or ("route_name" in data)
