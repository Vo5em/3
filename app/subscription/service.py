from .client import get_json
from .node_client import get_nodes
from .parser import parse_subscription
from .filter import filter_endpoints
from .builder import SubscriptionBuilder
from .generator import SubscriptionGenerator


async def build_subscription(sub_id: str):

    print("\n========== SUBSCRIPTION DEBUG ==========")

    # =====================================================
    # 1. Получаем исходную подписку
    # =====================================================

    json_data = await get_json(sub_id)

    print("JSON DATA TYPE:", type(json_data))

    if isinstance(json_data, list):
        print("JSON DATA LENGTH:", len(json_data))

        for i, item in enumerate(json_data):
            print(
                f"SOURCE {i}:",
                item.get("remarks")
            )

    else:
        print("SOURCE IS NOT LIST")
        print(json_data)

    # =====================================================
    # 2. Парсим endpoint'ы
    # =====================================================

    endpoints = parse_subscription(json_data)

    print("ENDPOINTS BEFORE FILTER:", len(endpoints))

    for endpoint in endpoints:
        print(
            "ENDPOINT:",
            endpoint.country,
            endpoint.protocol,
            endpoint.address
        )

    # =====================================================
    # 3. Получаем состояние узлов
    # =====================================================

    nodes = await get_nodes()

    print("NODES:", len(nodes))

    for node in nodes:
        print(
            "NODE:",
            node.get("name"),
            node.get("address"),
            "STATUS:",
            node.get("status"),
            "CPU:",
            node.get("cpuPct"),
            "RAM:",
            node.get("memPct"),
            "XRAY:",
            node.get("xrayState")
        )

    # =====================================================
    # 4. Фильтруем endpoint'ы
    # =====================================================

    endpoints = filter_endpoints(
        endpoints,
        nodes
    )

    print("ENDPOINTS AFTER FILTER:", len(endpoints))

    if not endpoints:
        raise ValueError(
            "После фильтрации не осталось доступных подключений"
        )

    for endpoint in endpoints:
        print(
            "ALLOWED:",
            endpoint.country,
            endpoint.protocol,
            endpoint.address
        )

    # =====================================================
    # 5. Строим страны
    # =====================================================

    countries = SubscriptionBuilder(
        endpoints
    ).build()

    print("COUNTRIES:", len(countries))

    for country in countries:
        print(
            "COUNTRY:",
            country.name,
            "ENDPOINTS:",
            len(country.endpoints)
        )

    # =====================================================
    # 6. Генерируем профили
    # =====================================================

    generator = SubscriptionGenerator(
        countries
    )

    result = generator.build()

    print("RESULT TYPE:", type(result))
    print("RESULT LENGTH:", len(result))

    for i, profile in enumerate(result):
        print(
            f"PROFILE {i}:",
            profile.get("remarks")
        )

    print("========================================\n")

    return result