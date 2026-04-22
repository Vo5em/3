from email.policy import default

from sqlalchemy import ForeignKey, String, BigInteger, DateTime, Boolean, false
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime
from zoneinfo import ZoneInfo
from config import DATABASE_URL

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    payload: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    notify_message: Mapped[int] = mapped_column(default=0)
    trial_used: Mapped[bool] = mapped_column(Boolean, default=False)


class Tariff(Base):
    __tablename__ = 'tariffs'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    type: Mapped[str] = mapped_column(String(20))
    duration_days: Mapped[int] = mapped_column()         # 30 / 90 / 180 / 365
    max_devices: Mapped[int] = mapped_column()
    traffic_limit: Mapped[int] = mapped_column(nullable=True)
    price: Mapped[int] = mapped_column()                 # Цена в выбранной валюте=


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariffs.id"))
    type: Mapped[str] = mapped_column(String(20))
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=False)
    payment_method_id = mapped_column(String(100), nullable=True)
    key: Mapped[str] = mapped_column(String(255), nullable=True)  # Сам ключ
    uuid: Mapped[str] = mapped_column(String(60), nullable=True)
    auto_renew: Mapped[bool] = mapped_column(default=False)
    traffic_used: Mapped[int] = mapped_column(default=0)# UUID для подключения



class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(50),default="pending")
    create_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(MOSCOW_TZ))
    type: Mapped[str] = mapped_column(String(50), nullable=True)
    payment_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)

class Servers(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # Имя сервера (удобный label)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    # URL панели → https://domain.com/ или https://x.x.x.x/
    base_url: Mapped[str] = mapped_column(String(120), nullable=False)
    # Адрес реального сервера (домен или IP)
    address: Mapped[str] = mapped_column(String(120), nullable=False)
    # Порт (обычно 443)
    port: Mapped[int] = mapped_column(nullable=False, default=443)
    # Reality параметры
    pbk: Mapped[str] = mapped_column(String(120), nullable=False)   # publicKey
    sni: Mapped[str] = mapped_column(String(120), nullable=False)
    sid: Mapped[str] = mapped_column(String(120), nullable=False)
    fp: Mapped[str] = mapped_column(String(60), nullable=False)     # fingerprint
    #login
    login: Mapped[str] = mapped_column(String(60), nullable=False)
    password: Mapped[str] = mapped_column(String(60), nullable=False)

    # Активен ли сервер
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)


class UserServer(Base):
    __tablename__ = 'userserver'

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(String(60),nullable=True)
    server: Mapped[int] = mapped_column(BigInteger, nullable=True)



async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)