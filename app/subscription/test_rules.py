import asyncio
import json

from client import get_json
from parser import parse_subscription
from rules import find_builder


async def main():

    # Получаем настоящий JSON из 3x-ui
    json_data = await get_json(
        "2fde387b-1cda-46"
    )

    # Разбираем его на Endpoint
    endpoints = parse_subscription(
        json_data
    )

    print(f"Получено подключений: {len(endpoints)}")

    for index, endpoint in enumerate(
        endpoints,
        start=1
    ):

        print("=" * 60)

        print("Страна:", endpoint.country)
        print("Тип:", endpoint.protocol)
        print("Адрес:", endpoint.address)
        print("Порт:", endpoint.port)

        # Получаем исходный outbound из 3x-ui
        outbound = endpoint.config["outbounds"][0]

        # Находим правило для этого типа
        builder = find_builder(
            endpoint.protocol
        )

        # Преобразуем 3x-ui → Sing-box
        singbox_outbound = builder(
            outbound,
            f"server-{index}"
        )

        print("\nSing-box outbound:")

        print(
            json.dumps(
                singbox_outbound,
                indent=4,
                ensure_ascii=False
            )
        )


asyncio.run(main())