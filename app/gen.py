import httpx
import uuid
import base64
import json
from app.database.requests import set_key, cheng_state_d, findd_tarif, cheng_state_a
from app.database.models import async_session, Servers, UserServer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config import SUB_DOMAIN
from fastapi import APIRouter

router = APIRouter()




async def get_servers():
    async with async_session() as session:
        result = await session.execute(select(Servers))
        servers = result.scalars().all()

    server_dicts = []
    for s in servers:
        server_dicts.append({
            "id": s.id,
            "name": s.name,
            "base_url": s.base_url,
            "address": s.address,
            "port": s.port,
            "pbk": s.pbk,
            "sni": s.sni,
            "sid": s.sid,
            "fp": s.fp,
            "enabled": s.enabled,
            "login": s.login,
            "password": s.password
        })

    return server_dicts

async def plusserverid(uuid, pull):
    async with async_session() as session:
        session.add(UserServer(uuid=uuid, server=pull))
        await session.commit()


async def serch_pull(uuid):
    async with async_session() as session:
        result = await session.execute(
            select(UserServer.server)
            .where(UserServer.uuid == uuid)
        )

        servers = result.scalars().all()
    return servers


async def addkey(user_id, tarif):
    user_uuid = str(uuid.uuid4())
    sub_id = str(uuid.uuid4())[:16]
    servers = await get_servers()
    limit = await findd_tarif(tarif)


    for srv in servers:
        if not srv["enabled"]:
            continue
        client_email = f"{srv['name']}-{user_uuid[:8]}"

        async with httpx.AsyncClient(base_url=srv["base_url"], timeout=10.0) as client:


            login_resp = await client.post("login", json={
                "username": srv["login"],
                "password": srv["password"]
            })

            if login_resp.status_code != 200:
                print(f"Ошибка логина {srv['name']}")
                continue

            payload = {
                "id": 1,
                "settings": json.dumps({
                    "clients": [{
                        "id": user_uuid,
                        "email": client_email,
                        "flow": "xtls-rprx-vision",
                        "fingerprint": srv["fp"],
                        "shortId": srv["sid"],
                        "subId": sub_id, # один на все
                        "limitIp": limit['max_devices'],
                        "enable": True
                    }]
                }),
                "streamSettings": json.dumps({
                    "network": "tcp",
                    "security": "reality",
                    "realitySettings": {
                        "publicKey": srv["pbk"],
                        "fingerprint": srv["fp"],
                        "serverNames": [srv["sni"]],
                        "shortIds": [srv["sid"]],
                        "spiderX": "/"
                    }
                })
            }

            resp = await client.post("panel/api/inbounds/addClient", json=payload)

            if resp.status_code != 200:
                print(f"Ошибка клиента на {srv['name']}: {resp.text}")
                continue
            else:
                await plusserverid(user_uuid, srv["id"])


    subscription_url = f"https://{SUB_DOMAIN}/sub/{user_uuid}"

    await set_key(user_id, subscription_url, user_uuid, tarif)

async def delkey(user_uuid: str, tarif_id):

    servers = await get_servers()
    limit = await findd_tarif(tarif_id)
    final_server_ids = set(await serch_pull(user_uuid))

    for srv in servers:
        client_email = f"{srv['name']}-{user_uuid[:8]}"
        if srv["id"] not in final_server_ids:
            continue
        async with httpx.AsyncClient(base_url=srv["base_url"], timeout=10.0) as client:


            login_resp = await client.post("login", json={
                "username": srv["login"],
                "password": srv["password"]
            })

            if login_resp.status_code != 200:
                print(f"[{srv['name']}] Ошибка логина")
                continue


            payload = {
                "id": 1,
                "settings": json.dumps({
                    "clients": [{
                        "id": user_uuid,
                        "email": client_email,
                        "flow": "xtls-rprx-vision",
                        "fingerprint": srv["fp"],
                        "shortId": srv["sid"],
                        "limitIp": limit['max_devices'],
                        "enable": False
                    }]
                })
            }


            resp = await client.post(f"panel/api/inbounds/updateClient/{user_uuid}", json=payload)

            try:
                resp_json = resp.json()
            except Exception:
                print(f"Ошибка {resp.status_code}: {resp.text}")

            if resp_json.get("success"):
                print(f"Пользователь {client_email} отключён")
            else:
                print(f"Ошибка API: {resp_json}")
    await cheng_state_d(user_uuid)

async def activatekey(user_uuid: str, tarif_id):
    from app.database.requests import findd_tarif
    limit = await findd_tarif(tarif_id)
    servers = await get_servers()
    final_server_ids = set(await serch_pull(user_uuid))

    for srv in servers:
        client_email = f"{srv['name']}-{user_uuid[:8]}"
        if srv["id"] not in final_server_ids:
            continue


        base_url = srv["base_url"]
        if not base_url.startswith(("http://", "https://")):
            base_url = "http://" + base_url

        async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:


            login_resp = await client.post("login", json={
                "username": srv["login"],
                "password": srv["password"]
            })

            if login_resp.status_code != 200:
                print(f"[{srv['name']}]  Ошибка авторизации: {login_resp.text}")
                continue


            payload = {
                "id": 1,
                "settings": json.dumps({
                    "clients": [{
                        "id": user_uuid,
                        "email": client_email,
                        "flow": "xtls-rprx-vision",
                        "fingerprint": srv["fp"],
                        "shortId": [srv["sid"]],
                        "limitIp": limit['max_devices'],
                        "enable": True
                    }]
                })
            }


            resp = await client.post(
                f"panel/api/inbounds/updateClient/{user_uuid}",
                json=payload
            )

            try:
                j = resp.json()
            except:
                print(f"[{srv['name']}] Ошибка активации {resp.status_code}: {resp.text}")
                continue

            if j.get("success"):
                print(f"[{srv['name']}]  Пользователь {client_email} активирован")
            else:
                print(f"[{srv['name']}] Ответ API: {j}")
    await cheng_state_a(user_uuid)


'''
import asyncio
import uuid
import httpx

PANEL_URL = ''

API_TOKEN = ''

SUB_DOMAIN = ''


async def addkey(user_id: int):
    user_uuid = str(uuid.uuid4())
    sub_id = str(uuid.uuid4())[:16]

    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }

    async with httpx.AsyncClient(
        base_url=PANEL_URL,
        headers=headers,
        timeout=20
    ) as client:

        # Получаем список всех inbound
        resp = await client.get("/panel/api/inbounds/list")

        if resp.status_code != 200:
            raise Exception(resp.text)

        result = resp.json()

        if not result["success"]:
            raise Exception(result["msg"])

        inbound_ids = [
            inbound["id"]
            for inbound in result["obj"]
            if inbound["enable"]
        ]

        payload = {
            "client": {
                "email": f"tg_{user_id}",        
                "id": '7781cfd0-69e4-440c-81c7-6169dc90fcce',                 
                "subId": '2fde387b-1cda-46',                
                "flow": "xtls-rprx-vision",
                "limitIp": 8,
                "enable": False
            },
            "inboundIds": inbound_ids
        }

        resp = await client.post(
            f"/panel/api/clients/update/tg_{user_id}",
            json=payload
        )

        if resp.status_code != 200:
            raise Exception(resp.text)

        result = resp.json()

        if not result["success"]:
            raise Exception(result["msg"])

    subscription_url = f"https://{SUB_DOMAIN}:2096/sub/{sub_id}"
    print(subscription_url)
#    await set_key(
#        user_id=user_id,
#        key=subscription_url,
#        uuid=user_uuid,
#        tarif=tarif
#    )


if name == "__main__":
    asyncio.run(addkey(123456789))
'''