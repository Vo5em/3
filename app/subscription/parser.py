from .models import Endpoint


def parse_subscription(data: list[dict]) -> list[Endpoint]:

    endpoints = []

    for item in data:

        outbound = item["outbounds"][0]
        settings = outbound["settings"]


        country, protocol = item["remarks"].split("|", 1)

        endpoint = Endpoint(
            country=country,
            protocol=protocol,
            address=settings["address"],
            port=settings["port"],
            config=item
        )

        endpoints.append(endpoint)

    return endpoints