from copy import deepcopy

from .models import Country
from .rules import find_builder


class SubscriptionGenerator:

    def __init__(self, countries: list[Country]):
        self.countries = countries

    def _build_config(
        self,
        countries: list[Country],
        profile_name: str,
        use_global_balancer: bool = False,
    ) -> dict:

        if not countries:
            raise ValueError(
                f"Невозможно создать конфигурацию '{profile_name}': "
                "нет стран"
            )

        # Берём общие системные настройки
        # из первого исходного JSON.
        template = countries[0].endpoints[0].config

        outbounds = []

        all_endpoint_tags = []
        observatory_selectors = []

        country_balancers = []

        # =====================================================
        # Реальные подключения
        # =====================================================

        for country_index, country in enumerate(countries):

            country_tags = []

            for endpoint_index, endpoint in enumerate(
                country.endpoints
            ):

                source_outbound = (
                    endpoint.config["outbounds"][0]
                )

                builder = find_builder(
                    endpoint.protocol
                )

                tag = (
                    f"country-{country_index}-"
                    f"endpoint-{endpoint_index}"
                )

                xray_outbound = builder(
                    source_outbound,
                    tag
                )

                outbounds.append(
                    xray_outbound
                )

                country_tags.append(tag)
                all_endpoint_tags.append(tag)

            # =================================================
            # Если в стране несколько подключений —
            # создаём её собственный leastPing balancer
            # =================================================

            if len(country_tags) > 1:

                country_balancers.append({
                    "tag": country.name,

                    "selector": [
                        f"country-{country_index}-"
                    ],

                    "strategy": {
                        "type": "leastPing"
                    }
                })

                observatory_selectors.append(
                    f"country-{country_index}-"
                )

        # =====================================================
        # Observatory
        # =====================================================

        observatory = {
            "subjectSelector": observatory_selectors,
            "probeUrl": (
                "https://www.gstatic.com/"
                "generate_204"
            ),
            "probeInterval": "10s",
            "enableConcurrency": True
        }

        # =====================================================
        # Routing
        # =====================================================

        routing = {
            "domainStrategy": "AsIs",
            "rules": []
        }

        # =====================================================
        # Глобальный AUTO
        # =====================================================

        if use_global_balancer:

            global_balancer = {
                "tag": "🚀 Авто",

                "selector": [
                    "country-"
                ],

                "strategy": {
                    "type": "leastPing"
                }
            }

            routing["balancers"] = [
                global_balancer
            ]

            routing["rules"].append({
                "network": "tcp,udp",
                "balancerTag": "🚀 Авто"
            })

            observatory["subjectSelector"] = [
                "country-"
            ]

        # =====================================================
        # Конфигурация конкретной страны
        # =====================================================

        else:

            country = countries[0]

            country_index = 0

            country_tags = [
                f"country-{country_index}-"
                f"endpoint-{i}"
                for i in range(
                    len(country.endpoints)
                )
            ]

            # Если несколько подключений —
            # используем leastPing.
            if len(country_tags) > 1:

                routing["balancers"] = [
                    {
                        "tag": country.name,

                        "selector": [
                            "country-0-"
                        ],

                        "strategy": {
                            "type": "leastPing"
                        }
                    }
                ]

                routing["rules"].append({
                    "network": "tcp,udp",
                    "balancerTag": country.name
                })

            # Если подключение одно —
            # балансер вообще не нужен.
            else:

                routing["rules"].append({
                    "network": "tcp,udp",
                    "outboundTag": country_tags[0]
                })

        # =====================================================
        # Собираем итоговый Xray config
        # =====================================================

        config = {
            "dns": deepcopy(
                template.get("dns", {})
            ),

            "inbounds": deepcopy(
                template.get("inbounds", [])
            ),

            "log": deepcopy(
                template.get("log", {})
            ),

            "outbounds": outbounds,

            "policy": deepcopy(
                template.get("policy", {})
            ),

            "stats": deepcopy(
                template.get("stats", {})
            ),

            "observatory": observatory,

            "remarks": f"{profile_name}",

            "routing": routing
        }

        return config

    # =========================================================
    # PUBLIC BUILD
    # =========================================================

    def build(self) -> list[dict]:

        if not self.countries:
            raise ValueError(
                "Нет стран в подписке"
            )

        profiles = []

        # =====================================================
        # 1. Глобальный AUTO
        # =====================================================

        profiles.append(
            self._build_config(
                countries=self.countries,
                profile_name="🚀 Авто",
                use_global_balancer=True
            )
        )

        # =====================================================
        # 2. Отдельные страны
        # =====================================================

        for country in self.countries:

            profiles.append(
                self._build_config(
                    countries=[country],
                    profile_name=country.name,
                    use_global_balancer=False
                )
            )

        return profiles