import base64
from tarfile import is_tarfile

import httpx
import asyncio
import uuid
from fastapi import FastAPI, Request
from app.database.models import async_session, User, Order, Subscription,Tariff
from app.database.requests import find_sub, add_tarif_id
from app.notification import notify_before_end, notify_spss, notify_end
from zoneinfo import ZoneInfo
from sqlalchemy import select, update, delete, desc
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from yookassa import Payment, Configuration
from config import yookassa_shopid, yookassa_api, mybot
from app.gen2 import activatekey

MOSCOW_TZ = ZoneInfo("Europe/Moscow")
scheduler = AsyncIOScheduler(timezone=MOSCOW_TZ)

Configuration.account_id = yookassa_shopid
Configuration.secret_key = yookassa_api

app = FastAPI()


async def create_payment(tg_id: int, amount: float,tariff_id: int, currency: str = "RUB"):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            raise ValueError("Пользователь не найден")

        if not user.payload:
            user.payload = str(uuid.uuid4())
        payload_value = user.payload

        now = datetime.now(tz=MOSCOW_TZ)
        order = Order(user_id=user.id, create_at=now, status="pending")
        session.add(order)
        await session.commit()
        await session.refresh(order)
        order_id = order.id
        subb = await find_sub(tg_id)
        if not subb:
            sub = Subscription(user_id = user.id, tariff_id = tariff_id)
            session.add(sub)
            await session.commit()
            await session.refresh(sub)
        else:
            await add_tarif_id(user.tg_id, tariff_id)


    def _sync_create():
        return Payment.create({
            "amount": {"value": f"{amount:.2f}", "currency": currency},
            "capture": True,
            "confirmation": {"type": "redirect", "return_url": str(mybot)},
            "description": f"Оплата подписки для {tg_id}",
            "save_payment_method": True,
            "metadata": {"payload": payload_value},
        })

    payment = await asyncio.to_thread(_sync_create)
    payment_id = str(payment.id)
    payment_url = payment.confirmation.confirmation_url

    # Сохраняем payment_id в заказе
    async with async_session() as session:
        order = await session.get(Order, order_id)
        order.payment_id = payment_id
        await session.commit()

    print(f"[LOG] Created payment: {payment_id}, order_id: {order_id}")
    return payment_url

@app.post("/yookassa/webhook")
async def yookassa_webhook(request: Request):
    raw = await request.body()
    print("RAW webhook:", raw.decode())  # для отладки

    data = await request.json()
    event = data.get("event")
    obj = data.get("object", {})

    if event == "payment.succeeded":
        payload = obj.get("metadata", {}).get("payload")
        payment_method_id = obj.get("payment_method", {}).get("id")

        if payload:
            async with async_session() as session:
                results = await session.execute(select(User).where(User.payload == payload))
                user = results.scalars().first()
                result = await session.execute(select(Subscription).where(Subscription.user_id == user.id))
                sub = result.scalars().first()
                if not sub.end_date:
                    await addkey(user.tg_id, sub.tariff_id)

                now = datetime.now(tz=MOSCOW_TZ)
                tarif = findd_tarif(sub.tariff_id)
                if sub.end_date < now:
                    sub.end_date = now + timedelta(days=tarif.duration_days)
                else:
                    sub.end_date += timedelta(days=tarif.duration_days)

                ruuid = sub.uuid
                tg_id = int(user.tg_id)
                iid = user.id
                ref_id = user.referrer_id


                await activatekey(ruuid)
                try:
                    await notify_spss(tg_id)
                    await plusnoty(tg_id)
                except Exception as e:
                    print(f"Ошибка при notify_spss: {e}")
                if ref_id is not None:
                    await maketake(iid, ref_id)
                else:
                    print("User has no referrer, skipping takeprise")


                if payment_method_id:
                    user.payment_method_id = payment_method_id

                result = await session.execute(
                    select(Order)
                    .where(Order.user_id == user.id)
                    .order_by(Order.create_at.desc())
                )
                order = result.scalars().first()
                if order:
                    order.status = "paid"

                await session.commit()


    elif event == "payment.canceled":
        payload = obj.get("metadata", {}).get("payload")

        if payload:
            async with async_session() as session:
                result = await session.execute(
                    select(User).where(User.payload == payload)
                )
                user = result.scalars().first()
                if not user:
                    return {"status": "user_not_found"}

                result = await session.execute(
                    select(Order)
                    .where(Order.user_id == user.id)
                    .order_by(Order.create_at.desc())
                )
                order = result.scalars().first()
                if order:
                    order.status = "canceled"

                await session.commit()

    return {"status": "ok"}

async def disable_autopay_if_failed():
    now = datetime.now(tz=MOSCOW_TZ)

    async with async_session() as session:
        result = await session.execute(
            select(User, Subscription)
            .join(Subscription)
            .where(
                Subscription.end_date < now,
                Subscription.is_active.is_(True),
                User.payment_method_id != None
            )
        )

        for user, sub in result.all():

            # Ищем последний заказ
            last_order = await session.scalar(
                select(Order)
                .where(Order.user_id == user.id)
                .order_by(Order.create_at.desc())
            )

            # 👉 Проверяем что была неудачная попытка оплаты
            if last_order and last_order.status == "canceled":
                user.payment_method_id = None


        await session.commit()


async def create_auto_payment(user: User,session, amount, currency: str = "RUB"):
    if not user.payment_method_id:
        raise ValueError("Нет сохранённого способа оплаты")

    payment = Payment.create({
        "amount": {
            "value": f"{amount:.2f}",
            "currency": currency
        },
        "capture": True,
        "payment_method_id": user.payment_method_id,  # ключ для автосписания
        "description": f"Автопродление подписки {user.tg_id}",
        "metadata": {
            "payload": user.payload,
            "type": "auto"
        }
    })
    order = Order(
        user_id=user.id,
        payment_id=payment.id,
        status=payment.status,  # pending / succeeded
        type="auto"
    )

    session.add(order)

    return payment.id

@app.get("/")
async def index(request: Request):
    return {"message": "Hello"}