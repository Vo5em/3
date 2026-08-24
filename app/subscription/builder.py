from .models import Country, Endpoint
from .selector import select_best_endpoint


class SubscriptionBuilder:

    def __init__(self, endpoints: list[Endpoint]):

        self.endpoints = endpoints

    def build(self) -> list[Country]:

        countries = {}

        for endpoint in self.endpoints:

            if endpoint.country not in countries:

                countries[endpoint.country] = Country(
                    name=endpoint.country
                )

            countries[endpoint.country].endpoints.append(endpoint)

        # Выбираем лучшее подключение
        for country in countries.values():

            country.selected_endpoint = select_best_endpoint(
                country.endpoints
            )

        return list(countries.values())