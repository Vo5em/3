from .models import Endpoint


def select_best_endpoint(endpoints: list[Endpoint]) -> Endpoint | None:

    if not endpoints:
        return None

    return endpoints[0]