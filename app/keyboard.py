from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from app.database.models import Subscription, User, async_session

st_choice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продолжить', callback = 'next')],
    [InlineKeyboardButton(text='У меня есть аккаунт', callback = 'estakk')]
])

main_pr = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Купить', callback_data='pay')],
    [InlineKeyboardButton(text= 'Получить пробный период', callback_data='probnik')],
    [InlineKeyboardButton(text='Реферальная программа', callback_data='refka')],
    [InlineKeyboardButton(text='Помощь', callback_data='help')]
])

main_out = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text= 'Оплата / Продление',callback_data='pay')],
    [InlineKeyboardButton(text='Реферальная программа',callback_data='refka')],
    [InlineKeyboardButton(text='Помощь',callback_data='help')]
])


main_old = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text= 'Оплата / Продление',callback_data='pay')],
    [InlineKeyboardButton(text='Доступы',callback_data='period')],
    [InlineKeyboardButton(text='Реферальная программа',callback_data='refka')],
    [InlineKeyboardButton(text='Помощь',callback_data='help')]
])


main_legend = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text= 'Оплата / Продление',callback_data='pay'),
     InlineKeyboardButton(text= 'Получить пробный период', callback_data='probnik')],
    [InlineKeyboardButton(text='Доступы',callback_data='period')],
    [InlineKeyboardButton(text='Реферальная программа',callback_data='refka')],
    [InlineKeyboardButton(text='Помощь',callback_data='help')]
])

netvbdemail = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Новый аккаунт', callback_data='next')],
    [InlineKeyboardButton(text='Попробовать еще раз', callback_data='estakk')]
])

retrycode = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = 'Отправить код еще раз', callback_data='recode')],
    [InlineKeyboardButton(text = 'Изменить почту', callback_data = 'estakk')]
])

tryagain = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = 'Отправить код еще раз', callback_data = 'recode')]
])

helps = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Поддержка',url='https://t.me/Rokoppo')],
    [InlineKeyboardButton(text='⬅Назад',callback_data='home')]
])

prob = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Активировать', callback_data='doitpls_1')],
    [InlineKeyboardButton(text='⬅Назад', callback_data= 'home')]
])

gadgets = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Android', callback_data='android'),
     InlineKeyboardButton(text='Iphone', callback_data='iphone')],
    [InlineKeyboardButton(text='Huawei', callback_data='huawei'),
     InlineKeyboardButton(text='Windows', callback_data='windows')],
    [InlineKeyboardButton(text='MacOS', callback_data='macos'),
     InlineKeyboardButton(text='Android TV', callback_data='androidtv')]
])


downloadand = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скачать приложение',
                          url='https://play.google.com/store/apps/details?id=com.v2raytun.android')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='period'),
     InlineKeyboardButton(text='Видео инструкция', url='https://t.me/e_instructions/17')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


downloadiph = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скачать приложение', url='https://apps.apple.com/lt/app/v2raytun/id6476628951')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='period'),
     InlineKeyboardButton(text='Видео инструкция', url='https://t.me/e_instructions/4')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


downloadHUA = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скачать приложение', url='https://www.youtube.com/watch?v=CW5oGRx9CLM')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='period')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


downloaddich = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скачать приложение', url='https://www.youtube.com/watch?v=CW5oGRx9CLM')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='period'),
     InlineKeyboardButton(text='Видео инструкция', url='https://www.youtube.com/watch?v=CW5oGRx9CLM')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


downloadwin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скачать приложение', url='https://github.com/MatsuriDayo/nekoray/releases'
                                                         '/download/4.0.1/nekoray-4.0.1-2024-12-12-windows64.zip')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='period'),
     InlineKeyboardButton(text='Видео инструкция', url='https://www.youtube.com/watch?v=CW5oGRx9CLM')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


downloadTV = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пульт для Android', url='https://play.google.com'
                                                        '/store/apps/details?id=tech.simha.androidtvremote&hl=en_US'),
     InlineKeyboardButton(text='Пульт для Iphone', url='https://apps.apple.com'
                                                       '/ru/app/remote-for-android-tv/id1668755298')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='period')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


go_home = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='⬅Назад', callback_data='home')]
])


on_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])


choose_type = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Белые списки', callback_data=''),
     InlineKeyboardButton(text='Стандарт', callback_data='pay')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='home')]
])


go_pay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оформить подписку', callback_data='pay')]
])

optionssub = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = 'Перейти к подключению', callback_data='period')],
    [InlineKeyboardButton(text = 'Продлить', callback_data='')],
    [InlineKeyboardButton(taxt = 'Переименовать', callback_data='')],
    [InlineKeyboardButton(text = '⬅ К списку подписок', callback_data='')]
])


give_money_1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1 месяц', callback_data='doitpls_2'),
    InlineKeyboardButton(text = '3 месяца', callback_data = 'doitpls_3')],
    [InlineKeyboardButton(text = '6 месяцев', callback_data = 'doitpls_4'),
     InlineKeyboardButton(text='12 месяцев', callback_data = 'doitpls_5')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='home')]
])

give_money_2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text= '7 дней', callback_data = 'doitpls_1')],
    [InlineKeyboardButton(text='1 месяц', callback_data='doitpls_2'),
    InlineKeyboardButton(text = '3 месяца', callback_data = 'doitpls_3')],
    [InlineKeyboardButton(text = '6 месяцев', callback_data = 'doitpls_4'),
     InlineKeyboardButton(text='12 месяцев', callback_data = 'doitpls_5')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='home')]
])



gadgets_old = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Android', callback_data='android'),
     InlineKeyboardButton(text='Iphone', callback_data='iphone')],
    [InlineKeyboardButton(text='Huawei', callback_data='huawei'),
     InlineKeyboardButton(text='Windows', callback_data='windows')],
    [InlineKeyboardButton(text='MacOS', callback_data='macos'),
     InlineKeyboardButton(text='Android TV', callback_data='androidtv')],
    [InlineKeyboardButton(text='⬅Назад', callback_data='home')]
])


admin = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='рассылка всем пользователям', callback_data='send_all')],
    [InlineKeyboardButton(text='рассылка только платикам', callback_data='send_vip')],
    [InlineKeyboardButton(text='рассылка только броукам', callback_data='send_broke')],
    [InlineKeyboardButton(text='↩️На главную', callback_data='home')]
])

admin_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
])

cancelautopay = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1 устройство', callback_data='one'),
    InlineKeyboardButton(text='2 устройства', callback_data='two')],
    [InlineKeyboardButton(text='5 устройств', callback_data='five')],
    [InlineKeyboardButton(text='Отмена авотпродления', callback_data="plsno")],
    [InlineKeyboardButton(text='⬅Назад', callback_data='home')]
])

def payment_keyboard(payurl: str, iid: int) -> InlineKeyboardMarkup:
    if iid <= 5:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", url=payurl)],
            [InlineKeyboardButton(text="⬅Назад", callback_data="one")]
        ])
    elif 5 < iid <= 9:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", url=payurl)],
            [InlineKeyboardButton(text="⬅Назад", callback_data="two")]
        ])
    else:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", url=payurl)],
            [InlineKeyboardButton(text="⬅Назад", callback_data="five")]
        ])

async def subscriptions_keyboard_trail(tg_id: int) -> InlineKeyboardMarkup:
    async with async_session() as session:
        user_id = await session.scalar(
            select(User.id).where(User.tg_id == tg_id)
        )

        if not user_id:
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅ Назад", callback_data="main")]
            ])

        result = await session.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subs = result.scalars().all()


    if not subs:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Нет подписок", callback_data="noop")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="main")]
        ])


    keyboard = []

    for sub in subs:
        text = f""
        if sub.name:


            if sub.is_active:
                text +=  f"🟢 {sub.name} • {sub.type}"
            else:
                text += f"🔴 {sub.name} • {sub.type}"
        else:
            if sub.is_active:
                text +=  f"🟢 {sub.uuid[8:]} • {sub.type}"
            else:
                text += f"🔴 {sub.uuid[8:]} • {sub.type}"


        keyboard.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"subtr_{sub.id}"
            )
        ])


    keyboard.append([
        InlineKeyboardButton(text="⬅ Назад", callback_data="main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def subscriptions_keyboard(tg_id: int) -> InlineKeyboardMarkup:
    async with async_session() as session:
        user_id = await session.scalar(
            select(User.id).where(User.tg_id == tg_id)
        )

        if not user_id:
            return InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅ Назад", callback_data="main")]
            ])

        result = await session.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subs = result.scalars().all()


    if not subs:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Нет подписок", callback_data="noop")],
            [InlineKeyboardButton(text="⬅ Назад", callback_data="main")]
        ])


    keyboard = []

    for sub in subs:
        text = f""
        if sub.name != None:


            if sub.is_active:
                text +=  f"🟢 {sub.name} • {sub.type}"
            else:
                text += f"🔴 {sub.name} • {sub.type}"
        else:
            if sub.is_active:
                text +=  f"🟢 {sub.uuid[8:]} • {sub.type}"
            else:
                text += f"🔴 {sub.uuid[8:]} • {sub.type}"


        keyboard.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"sub_{sub.id}"
            )
        ])


    keyboard.append([
        InlineKeyboardButton(text="⬅ Назад", callback_data="main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def infpodpiska(idd: int) -> InlineKeyboardMarkup:
    keyboard = []
    keyboard.append([
        InlineKeyboardButton(
            text=f'Настройки подключения',
            callback_data=f"sub_{idd}"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)




