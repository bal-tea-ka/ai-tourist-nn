import httpx
from app.config import settings

API_KEY = settings.PERPLEXITY_API_KEY

async def call_perplexity(prompt: str, domain_filter=None) -> str:
    headers = {"Authorization": f"Bearer {API_KEY}"}
    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "You are tourism assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    if domain_filter:
        payload["search_domain_filter"] = domain_filter

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post("https://api.perplexity.ai/chat/completions", json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
