import httpx
from config import SUB_URL



async def get_json(sub_id: str) -> list:

    try:

        async with httpx.AsyncClient(timeout=20) as client:

            response = await client.get(
                f"{SUB_URL}/json/{sub_id}"
            )

            response.raise_for_status()

            return response.json()

    except httpx.HTTPStatusError as e:

        raise Exception(
            f"Не удалось получить подписку ({e.response.status_code})"
        )

    except httpx.RequestError:

        raise Exception(
            "Не удалось подключиться к серверу подписок"
        )