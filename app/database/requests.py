import base64
from tarfile import is_tarfile

import httpx
import asyncio
import uuid
from fastapi import FastAPI, Request
from app.database.models import async_session, User, Order, Subscription,Tariff
from app.notification import notify_before_end, notify_spss, notify_end
from zoneinfo import ZoneInfo
from sqlalchemy import select, update, delete, desc
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from yookassa import Payment, Configuration
from config import yookassa_shopid, yookassa_api, mybot
from app.gen2 import activatekey
from app.database.pay import create_auto_payment




MOSCOW_TZ = ZoneInfo("Europe/Moscow")
scheduler = AsyncIOScheduler(timezone=MOSCOW_TZ)

Configuration.account_id = yookassa_shopid
Configuration.secret_key = yookassa_api

app = FastAPI()


async def set_user(tg_id: int, ref_id: int = None):
    async with async_session() as session:
        # Проверяем, есть ли пользователь
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            # Новый пользователь
            referrer = None
            if ref_id:
                referrer = await session.scalar(select(User).where(User.tg_id == ref_id))

            new_user = User(
                tg_id=tg_id,
                referrer_id=referrer.id if referrer else None
            )
            session.add(new_user)
            await session.flush()  # чтобы new_user.id появился

            # Если есть валидный реферер, даём бонус к подписке
            if referrer:
                # Ищем активную подписку реферера
                active_sub = await session.scalar(
                    select(Subscription)
                    .where(Subscription.user_id == referrer.id)
                    .where(Subscription.is_active == True)
                )
                now_moscow = datetime.now(tz=MOSCOW_TZ)

                # Если есть активная подписка → продлеваем
                if active_sub:
                    if active_sub.end_date < now_moscow:
                        # подписка истекла — старт с текущего момента
                        active_sub.end_date = now_moscow + timedelta(days=7)
                        await activatekey(referrer.uuid)# бонус +7 дней
                    else:
                        # продлеваем текущую подписку
                        active_sub.end_date += timedelta(days=7)
                    session.add(active_sub)
        await session.commit()


async def set_key(tg_id, vless_link, new_uuid, tarif):
    async with async_session() as session:
        result = await session.execute(select(Tariff).where(Tariff.id == tarif))
        tariff = result.scalars().first()
        now_moscow = datetime.now(tz=MOSCOW_TZ)
        dayend = now_moscow + timedelta(days=tariff.duration_days)
        dayend_naive = dayend.replace(tzinfo=None)
        id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
        sub = Subscription(
            user_id=id,
            tariff_id=tarif,
            key = vless_link,
            uuid = new_uuid,
            end_date=dayend_naive,
            is_active=True
        )
        session.add(sub)
        await session.commit()


async def check_end():
    print("ger")
    from app.gen import delkey
    now_moscow = datetime.now(tz=MOSCOW_TZ)
    try:
        async with async_session() as session:
            end = await session.execute(select(Subscription.uuid).where
                                        (Subscription.end_date != None,
                                         Subscription.end_date < now_moscow,
                                         Subscription.is_active == True))
            results = end.all()
            if not results:
                return
            for uuid in results:
                await delkey(uuid)
            await session.commit()
    except Exception as e:
        print(f"Ошибка в check_end: {e}")

async def find_trial(tg_id):
    async with async_session() as session:
        find_trail = await session.scalar(select(User.trial_used).where(User.tg_id == tg_id))
        return find_trail

async def add_tarif_id(tg_id, tarif_id):
    async with async_session() as session:
        id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
        await session.execute(update(Subscription).where(Subscription.user_id == id).values(tariff_id = tarif_id))
        await session.commit()

async def find_tarif(tg_id):
    async with async_session() as session:
        id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
        tarif_id = await session.scalar(select(Subscription.tariff_id).where(Subscription.user_id == id))
        result= await session.execute(select(Tariff).where(Tariff.id == tarif_id))
        tarif = result.scalars().first()
        return tarif

async def findd_tarif(id):
    async with async_session() as session:
        result= await session.execute(select(Tariff).where(Tariff.id == id))
        tarif = result.scalars().first()
        return tarif


async def cheng_state_d(uuid):
    async with async_session() as session:
        await session.execute(update(Subscription).where(Subscription.uuid == uuid).values(is_active = False))
        await session.commit()

async def find_sub(tg_id):
    async with async_session() as session:
        id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
        sub = await session.scalar(select(Subscription.id).where(Subscription.id == id))
        return sub



async def get_users():
    async with async_session() as session:
        result = await session.scalars(select(User.tg_id))
        return result.all()


async def get_vip():
    async with async_session() as session:
        result = await session.execute(select(User.tg_id).where(User.payload != None))
        return [row[0] for row in result.all()]


async def get_broke():
    async with async_session() as session:
        result = await session.execute(select(User.tg_id).where(User.payload == None))
        return [row[0] for row in result.all()]


async def find_key(tg_id):
    async with async_session() as session:
        idd = await session.scalar(select(User.id).where(User.tg_id == tg_id))
        key = await session.scalar(select(Subscription.key).where(Subscription.user_id == idd))
        return key


async def find_dayend(tg_id):
    async with async_session() as session:
        id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
        day = await session.scalar(select(Subscription.end_date).where(Subscription.user_id == id))
    return day

async def plus_subtime(tg_id, tariff_id):
    async with async_session() as session:
        from app.gen import addkey
        id = await session.saclar(select(User.id).where(User.tg_id == tg_id))
        tarif = await findd_tarif(tariff_id)
        day = await find_dayend(tg_id)
        if not day:
            await addkey(tg_id, tariff_id)
        result = await session.execute(select(Subscription).where(Subscription.user_id == id))
        sub = result.scalars().all()
        now_moscow = datetime.now(tz=MOSCOW_TZ)
        if sub.end_date < now_moscow:
            dayend = now_moscow + timedelta(days = tarif.duretion_days)
            dayend_naive = dayend.replace(tzinfo=None)

        else:
            dayend = sub.end_date + timedelta(days = tarif.duretion_days)
            dayend_naive = dayend.replace(tzinfo=None)
        await session.execute(update(Subscription).where(Subscription.user_id == id).values(end_date = dayend_naive,
                                                                                            is_active = True))
        await session.commit()





async def find_tgid(id):
    async with async_session() as session:
        tg_id = await session.scalar(select(User.tg_id).where(User.id == id))
    return tg_id


async def maketake(iid, ref_id):
    async with async_session() as session:
        result = await session.execute(
            select(Order).where(Order.user_id == iid, Order.status == "paid")
        )
        paid_orders = result.scalars().all()

        if iid and len(paid_orders) <= 1:
            await takeprise(ref_id)


async def takeprise(ref_id2):
    async with async_session() as session:
         ref_check = await session.scalar(select(Subscription).where(Subscription.user_id == ref_id2))
         if ref_check:
            print("ger")
            new_daybalance = 7
            is_tgid = await find_tgid(ref_id2)
            is_day = await find_dayend(is_tgid)
            now_moscow = datetime.now(tz=MOSCOW_TZ)
            if is_day.tzinfo is None:
                is_day = is_day.replace(tzinfo=MOSCOW_TZ)
            if is_day < now_moscow:
                dayend = now_moscow + timedelta(days=new_daybalance)
                await session.execute(update(Subscription).where(Subscription.user_id == ref_id2).values(end_date=dayend,
                                                                                      is_active=True))
            else:
                dayend = is_day + timedelta(days=new_daybalance)
                await session.execute(update(Subscription).where(Subscription.user_id == ref_id2).values(end_date=dayend,
                                                                                      is_acteive=True))
         await session.commit()


async def find_payload(tg_id):
    async with async_session() as session:
        payload = await session.scalar(select(User.payload).where(User.tg_id == tg_id))
    return payload


async def save_message(tg_id, message_id):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalars().first()
        print("t")
        if user:
            user.message_id = message_id
        await session.commit()


async def find_message(tg_id):
    async with async_session() as session:
        message = await session.scalar(select(User.message_id).where(User.tg_id == tg_id))
    return message


async def find_paymethod_id(tg_id):
    async with async_session() as session:
        paymenthod_id = await session.scalar(select(User.payment_method_id).where
                                             (User.payment_method_id != None, User.tg_id == tg_id))
        return paymenthod_id


async def delpaymethod_id(tg_id):
    async with async_session() as session:
        paymenthod_id = await session.scalar(select(User.payment_method_id).where
                                             (User.payment_method_id != None, User.tg_id == tg_id)
                                             )
        if paymenthod_id:
            await session.execute(update(User).where(User.tg_id == tg_id).values(payment_method_id=None,
                                                                                 notify_message=0)
                                  )
        await session.commit()


async def schedulers():
    while True:
        try:
            print("geeer")
            await check_subscriptions()
            await check_end()
            await check_notyfy()
            await check_pending()
            await disable_autopay_if_failed()
        except Exception as e:
            print(f"Ошибка в schedulers(): {e}")
        await asyncio.sleep(1800)


async def check_pending():
    now = datetime.now(tz=MOSCOW_TZ)
    async with async_session() as session:
        await session.execute(
            update(Order).where(Order.create_at != None, Order.create_at <= now - timedelta(minutes=15),
                                Order.status == "pending").values(status="canceled")
        )
        await session.commit()


async def plusnoty(tg_id):
    async with async_session() as session:
        await session.execute(update(User).where(User.tg_id == tg_id).values(notify_message=2))
        await session.commit()


async def check_notyfy():
    print("sta")
    now_moscow = datetime.now(tz=MOSCOW_TZ)
    try:
        async with async_session() as session:
            # За 1 день до окончания
            result_before = await session.execute(
                select(User, Subscription).join(Subscription).where(
                    Subscription.end_date != None,
                    Subscription.end_date <= now_moscow + timedelta(days=1),
                    Subscription.end_date > now_moscow + timedelta(hours=1),
                    User.notify_message < 1,
                    Subscription.is_active.is_(True)
                )
            )

            for user, sub in result_before.all():
                await notify_before_end(user.tg_id)
                user.notify_message = 1

            # За 1 час до окончания
            result_end = await session.execute(
                select(User, Subscription).join(Subscription).where(
                    Subscription.end_date != None,
                    Subscription.end_date <= now_moscow + timedelta(hours=1),
                    Subscription.end_date >= now_moscow,
                    User.notify_message < 2,
                    Subscription.is_active.is_(True)
                )
            )

            for user, sub in result_end.all():
                await notify_end(user.tg_id)
                user.notify_message = 2

        await session.commit()

    except Exception as e:
        print(f'{e}')


async def check_subscriptions():
    print("g")
    now = datetime.now(tz=MOSCOW_TZ)
    try:
        async with async_session() as session:
            users = await session.execute(
                select(Subscription).where(Subscription.end_date != None,
                                           Subscription.end_date - timedelta(hours=1) <= now,
                                           Subscription.end_date >= now,
                                           Subscription.is_active.is_(True))
            )
            for user in users.scalars().all():
                result = await session.execute(
                    select(Order).where(
                        Order.user_id == user.id,
                        Order.status == "pending"
                    )
                )
                order = result.scalars().first()


                if order:
                    continue
                tarif = await find_tarif(user.tg_id)

                await create_auto_payment(user, session, tarif.price)

            await session.commit()
    except Exception as e:
        print(f"Ошибка в check_subscriptions: {e}")


async def disable_autopay_if_failed():
    print('dis')
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

@app.get("/")
async def index(request: Request):
    return {"message": "Hello"}

