from .models import Endpoint


def is_node_allowed(node: dict) -> bool:
    """
    Проверяет, можно ли использовать узел
    для новых подключений.

    На первом этапе используем:
    - enable
    - status
    - xrayState
    - CPU
    - RAM
    """

    if not node.get("enable", False):
        return False

    if node.get("status") != "online":
        return False

    if node.get("xrayState") != "running":
        return False

    cpu_pct = node.get("cpuPct")

    if cpu_pct is None:
        return False

    if cpu_pct >= 85:
        return False

    mem_pct = node.get("memPct")

    if mem_pct is None:
        return False

    if mem_pct >= 90:
        return False

    return True


def filter_endpoints(
    endpoints: list[Endpoint],
    nodes: list[dict],
) -> list[Endpoint]:
    """
    Убирает endpoint'ы, принадлежащие нездоровым узлам.

    Endpoint сопоставляется с узлом по address.
    """

    allowed_addresses = set()

    for node in nodes:

        if not is_node_allowed(node):
            continue

        address = node.get("address")

        if address:
            allowed_addresses.add(address)

    return [
        endpoint
        for endpoint in endpoints
        if endpoint.address in allowed_addresses
    ]