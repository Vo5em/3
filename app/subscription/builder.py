from models import Country, Endpoint


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

            countries[endpoint.country].endpoints.append(
                endpoint
            )

        return list(countries.values())