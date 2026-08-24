import httpx
from config import PANEL_URL, PANEL_API_TOKEN
async def get_nodes() -> list[dict]:

    try:

        async with httpx.AsyncClient(
            timeout=20
        ) as client:

            response = await client.get(
                f"{PANEL_URL}/panel/api/nodes/list",
                headers={
                    "Authorization": f"Bearer {PANEL_API_TOKEN}"
                }
            )

            response.raise_for_status()

            data = response.json()

            if not data.get("success"):
                raise Exception(
                    f"Ошибка API 3x-ui: "
                    f"{data.get('msg', 'Unknown error')}"
                )

            return data.get("obj", [])

    except httpx.HTTPStatusError as e:

        raise Exception(
            f"Не удалось получить список узлов "
            f"({e.response.status_code})"
        )

    except httpx.RequestError:

        raise Exception(
            "Не удалось подключиться к API 3x-ui"
        )

