from app.config import settings
import requests

API_KEY = settings.PERPLEXITY_API_KEY


def ask_openrouter(question: str, api_key: str) -> str:

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/ai-tourist-assistant",
        "X-Title": "Tourist Assistant"
    }

    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {"role": "user", "content": question}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"Ошибка API: {response.status_code} - {response.text}"

    except Exception as e:
        return f"Ошибка: {str(e)}"


if __name__ == "__main__":
    print("AI")
    print("=" * 50)
    answer = ask_openrouter(main_prompt, API_KEY)
    print("Ответ:")
    print(answer)
