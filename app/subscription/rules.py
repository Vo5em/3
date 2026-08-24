from collections.abc import Callable

Builder = Callable[[dict, str], dict]


def build_xray_passthrough(
    outbound: dict,
    tag: str
) -> dict:

    result = outbound.copy()

    result["tag"] = tag

    return result


RULES: dict[str, Builder] = {
    "VLESS_TCP": build_xray_passthrough,
    "HYS": build_xray_passthrough,
}


def find_builder(connection_type: str) -> Builder:

    builder = RULES.get(connection_type)

    if builder is None:
        raise ValueError(
            f"Неизвестный тип подключения: {connection_type}"
        )

    return builder






"""from collections.abc import Callable


Builder = Callable[[dict, str], dict]


def build_vless_tcp(outbound: dict, tag: str) -> dict:
    settings = outbound["settings"]
    stream = outbound.get("streamSettings", {})
    tls = stream.get("tlsSettings", {})

    result = {
        "type": "vless",
        "tag": tag,

        "server": settings["address"],
        "server_port": settings["port"],
        "uuid": settings["id"],
    }

    if settings.get("flow"):
        result["flow"] = settings["flow"]

    if tls:
        result["tls"] = {
            "enabled": True,
        }

        if tls.get("serverName"):
            result["tls"]["server_name"] = tls["serverName"]

        if tls.get("alpn"):
            result["tls"]["alpn"] = tls["alpn"]

        if tls.get("fingerprint"):
            result["tls"]["utls"] = {
                "enabled": True,
                "fingerprint": tls["fingerprint"],
            }

    return result


def build_hysteria2(outbound: dict, tag: str) -> dict:
    settings = outbound["settings"]
    stream = outbound.get("streamSettings", {})

    hysteria = stream.get("hysteriaSettings", {})
    tls_settings = stream.get("tlsSettings", {})

    result = {
        "type": "hysteria2",
        "tag": tag,

        "server": settings["address"],
        "server_port": settings["port"],
    }

    if hysteria.get("auth"):
        result["password"] = hysteria["auth"]

    if tls_settings:
        result["tls"] = {
            "enabled": True,
        }

        if tls_settings.get("serverName"):
            result["tls"]["server_name"] = tls_settings["serverName"]

        if tls_settings.get("alpn"):
            result["tls"]["alpn"] = tls_settings["alpn"]

    finalmask = stream.get("finalmask", {})
    udp = finalmask.get("udp", [])

    if udp:
        mask = udp[0]

        if mask.get("type") == "salamander":
            password = (
                mask
                .get("settings", {})
                .get("password")
            )

            if password:
                result["obfs"] = {
                    "type": "salamander",
                    "password": password,
                }

    return result


RULES: dict[str, Builder] = {
    "VLESS_TCP": build_vless_tcp,
    "HYS": build_hysteria2,
}


def find_builder(connection_type: str) -> Builder:

    builder = RULES.get(connection_type)

    if builder is None:
        raise ValueError(
            f"Неизвестный тип подключения: {connection_type}"
        )

    return builder"""