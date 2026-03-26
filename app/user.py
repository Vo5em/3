import re
import html
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, Command, CommandObject
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
from app.keyboard import payment_keyboard
import app.keyboard as kb
from app.gen import addkey

from app.database.requests import set_user, find_key, find_dayend, save_message, find_paymethod_id, change_trial
from app.database.requests import delpaymethod_id, find_trial, find_tarif, findd_tarif, find_sub, plus_subtime
from app.database.pay import create_payment
MOSCOW_TZ = ZoneInfo("Europe/Moscow")

user = Router()

file_id01="AgACAgIAAxkBAAMIaRiR-KRzzYnTb2Bim8fB1jKG-gYAApYOaxulBsFIS3wYfJSChDcBAAMCAAN3AAM2BA"
file_id02="AgACAgIAAxkBAAMEaRiR3vyWrOlSNVH8AlCIXNDG24QAApQOaxulBsFIIWWE4RlHRNMBAAMCAAN3AAM2BA"
file_id03="AgACAgIAAxkBAAMGaRiR63EUhOEY7XHJPAvo6QbPYdMAApUOaxulBsFIF1KdTXzq_wEBAAMCAAN5AAM2BA"

def escape_markdown(text: str) -> str:
    return re.sub(r'([_\*\[\]\(\)~`>#+\-=|{}.!])', r'\\\1', text)


@user.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    tg_id = message.from_user.id
    ref_id = command.args
    if ref_id and ref_id.isdigit():
        ref_id = int(ref_id)
        await set_user(tg_id, ref_id)
    else:
        await set_user(tg_id, None)

    is_key = await find_trial(tg_id)
    paymenthodid = await find_paymethod_id(tg_id)
    if is_key == False:
        is_sub = await find_sub(tg_id)
        if not is_sub:
            await message.answer(
                f"👤 Ваш ID: {tg_id}\n\n"
                f"📦 Ваш тариф: отсутствует\n"
                f"📡 Статус: Не активен\n\n"
                f"🎁 Бесплатный пробный период доступен!\n"
                f"Нажмите кнопку ниже, чтобы активировать пробный доступ и протестировать VPN\n"
                f"👇 Выберите действие ниже",
                parse_mode="HTML",
                reply_markup=kb.main_pr
            )
        else:
            tarif = await find_tarif(tg_id)
            is_day = await find_dayend(tg_id)

            if is_day.tzinfo is None:
                is_day = is_day.replace(tzinfo=MOSCOW_TZ)
            if not paymenthodid:
                await message.answer(
                    f"👤 Ваш ID: {tg_id}\n\n"
                    f"📦 Ваш тариф: {tarif.name}\n"
                    f"📱 Устройств: до {tarif.max_devices}\n\n"
                    f"📡 Статус: Активен\n"
                    f"📅 До: {is_day.strftime('%d.%m.%Y')}\n\n"
                    f"♻️ Автопродление: отключено ",
                    parse_mode="HTML",
                    reply_markup=kb.main_old)
            else:
                await message.answer(
                    f"👤 Ваш ID: {tg_id}\n\n"
                    f"📦 Ваш тариф: {tarif.name}\n"
                    f"📱 Устройств: до {tarif.max_devices}\n\n"
                    f"📡 Статус: Активен\n"
                    f"📅 До: {is_day.strftime('%d.%m.%Y')}\n\n"
                    f"♻️ Автопродление: включено",
                    parse_mode="HTML",
                    reply_markup=kb.main_old)

    else:
        is_day = await find_dayend(tg_id)
        now_moscow = datetime.now(tz=MOSCOW_TZ)

        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)

        if is_day < now_moscow:
            await message.answer(
                f"👤 Ваш ID: {tg_id}\n\n"
                f"📦 Ваш тариф: отсутствует\n"
                f"📡 Статус: Не активен\n\n"
                f"Чтобы продолжить пользоваться сервисом:\n"
                f"• Выберите тариф\n"
                f"• Активируйте подписку\n\n"
                f"⚡ Подключение занимает меньше 1 минуты\n\n"
                f"👇 Нажмите «Продлить / Оплатить»",
                parse_mode="HTML",
                reply_markup=kb.main_out
            )
        else:
            tarif = await find_tarif(tg_id)
            if not paymenthodid:
                await message.answer(
                f"👤 Ваш ID: {tg_id}\n\n"
                f"📦 Ваш тариф: {tarif.name}\n"
                f"📱 Устройств: до {tarif.max_devices}\n\n"
                f"📡 Статус: Активен\n"
                f"📅 До: {is_day.strftime('%d.%m.%Y')}\n\n"
                f"♻️ Автопродление: отключено ",
                parse_mode="HTML",
                reply_markup=kb.main_old)
            else:
                await message.answer(
                f"👤 Ваш ID: {tg_id}\n\n"
                f"📦 Ваш тариф: {tarif.name}\n"
                f"📱 Устройств: до {tarif.max_devices}\n\n"
                f"📡 Статус: Активен\n"
                f"📅 До: {is_day.strftime('%d.%m.%Y')}\n\n"
                f"♻️ Автопродление: включено",
                parse_mode="HTML",
                reply_markup=kb.main_old)


@user.callback_query(F.data == 'home')
async def home(callback: CallbackQuery):
    tg_id = callback.from_user.id
    is_key = await find_trial(tg_id)
    paymenthodid = await find_paymethod_id(tg_id)
    if is_key == False:
        is_sub = await find_sub(tg_id)
        if not is_sub:
            await callback.answer('')
            await callback.message.edit_text(
                f"👤 Ваш ID: {tg_id}\n\n"
                f"📦 Ваш тариф: отсутствует\n"
                f"📡 Статус: Не активен\n\n"
                f"🎁 Бесплатный пробный период доступен!\n"
                f"Нажмите кнопку ниже, чтобы активировать пробный доступ и протестировать VPN\n"
                f"👇 Выберите действие ниже",
                parse_mode="HTML",
                reply_markup=kb.main_pr
            )

        else:
            tarif = await find_tarif(tg_id)
            is_day = await find_dayend(tg_id)
            now_moscow = datetime.now(tz=MOSCOW_TZ)

            if is_day.tzinfo is None:
                is_day = is_day.replace(tzinfo=MOSCOW_TZ)

            if is_day > now_moscow:
                if not paymenthodid:
                    await callback.message.edit_text(
                        f"👤 Ваш ID: {tg_id}\n\n"
                        f"📦 Ваш тариф: {tarif.name}\n"
                        f"📱 Устройств: до {tarif.max_devices}\n\n"
                        f"📡 Статус: Активен\n"
                        f"📅 До: {is_day.strftime('%d.%m.%Y')}\n\n"
                        f"🎁 Бесплатный пробный период доступен!\n"
                        f"♻️ Автопродление: отключено ",
                        parse_mode="HTML",
                        reply_markup=kb.main_olld)
                else:
                    tarif = await find_tarif(tg_id)
                    await callback.message.edit_text(
                        f"👤 Ваш ID: {tg_id}\n\n"
                        f"📦 Ваш тариф: {tarif.name}\n"
                        f"📱 Устройств: до {tarif.max_devices}\n\n"
                        f"📡 Статус: Активен\n"
                        f"📅 До: {is_day.strftime('%d.%m.%Y')}\n\n"
                        f"🎁 Бесплатный пробный период доступен!\n"
                        f"♻️ Автопродление: включено",
                        parse_mode="HTML",
                        reply_markup=kb.main_olld)
            else:
                await callback.message.edit_text(
                    f"👤 Ваш ID: {tg_id}\n\n"
                    f"📦 Ваш тариф: отсутствует\n"
                    f"📡 Статус: Не активен\n\n"
                    f"🎁 Бесплатный пробный период доступен!\n"
                    f"Нажмите кнопку ниже, чтобы активировать пробный доступ и протестировать VPN\n"
                    f"⚡ Подключение занимает меньше 1 минуты\n\n"
                    f"👇 Выберите действие ниже",
                    parse_mode="HTML",
                    reply_markup=kb.main_pr
            )
    else:
        is_day = await find_dayend(tg_id)
        now_moscow = datetime.now(tz=MOSCOW_TZ)

        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)

        if is_day < now_moscow:
            await callback.message.edit_text(
                f"👤 Ваш ID: {tg_id}\n\n"
                f"📦 Ваш тариф: отсутствует\n"
                f"📡 Статус: Не активен\n\n"
                f"Чтобы продолжить пользоваться сервисом:\n"
                f"• Выберите тариф\n"
                f"• Активируйте подписку\n\n"
                f"⚡ Подключение занимает меньше 1 минуты\n\n"
                f"👇 Нажмите «Продлить / Оплатить»",
                parse_mode="HTML",
                reply_markup=kb.main_out
            )
        else:
            tarif = await find_tarif(tg_id)
            if not paymenthodid:
                await callback.message.edit_text(
                    f"👤 Ваш ID: {tg_id}\n\n"
                    f"📦 Ваш тариф: {tarif.name}\n"
                    f"📱 Устройств: до {tarif.max_devices}\n\n"
                    f"📡 Статус: Активен\n"
                    f"📅 До: {is_day.strftime('%d.%m.%Y')}\n\n"
                    f"♻️ Автопродление: отключено ",
                    parse_mode="HTML",
                    reply_markup=kb.main_old)
            else:
                await callback.message.edit_text(
                    f"👤 Ваш ID: {tg_id}\n\n"
                    f"📦 Ваш тариф: {tarif.name}\n"
                    f"📱 Устройств: до {tarif.max_devices}\n\n"
                    f"📡 Статус: Активен\n"
                    f"📅 До: {is_day.strftime('%d.%m.%Y')}\n\n"
                    f"♻️ Автопродление: включено",
                    parse_mode="HTML",
                    reply_markup=kb.main_old)


@user.callback_query(F.data == 'help')
async def helps(callback: CallbackQuery):
    tg_id = callback.from_user.id
    await callback.answer('')
    await callback.message.edit_text(
        f"<b>ID:</b> <code>{tg_id}</code>\n\n"
        f"Первым сообщением напиши свой ID\n"
        f"Дальше опиши проблему - и мы тебе поможем.",
        parse_mode="HTML",
        reply_markup=kb.helps
    )



@user.message(Command('help'))
async def cmd_help(message: Message):
    tg_id = message.from_user.id
    await message.answer(
        f"<b>ID:</b><code>{tg_id}</code>\n\n"
        f"Первым сообщением напиши свой ID\n"
        f"Дальше опиши проблему - и мы тебе поможем.",
        parse_mode="HTML",
        reply_markup=kb.helps
    )


@user.message(Command('subscribe'))
async def cmd_sub(message: Message):
    tg_id = message.from_user.id
    paymenthodid = await find_paymethod_id(tg_id)

    if not paymenthodid:
        is_day = await find_dayend(tg_id)
        now_moscow = datetime.now(tz=MOSCOW_TZ)
        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)

        if is_day < now_moscow:
            await message.answer(
                '<b>Абонемент не активен</b>\n\n'
                '<b>Подписка на месяц - 150₽</b>\n'
                '— Деньги будут списываться каждый месяц.\n'
                '— Отключить автопродление можно в любой момент в этом разделе.\n'
                '— При отключении доступ сохранится до конца оплаченного.\n\n'
                '<b>Важно знать:</b> подключаясь, Ты принимаешь условия\n'
                'ежемесячного списания.',
                parse_mode="HTML",
                reply_markup=kb.give_money
            )
        else:
            await message.answer(
                f"<b>Абонемент до {is_day.strftime('%d.%m.%Y')}</b>\n\n"
                f"<b>Подписка на месяц — 150₽</b>\n"
                f"— Деньги будут списываться каждый месяц.\n"
                f"— Отключить автопродление можно в любой момент в этом разделе.\n"
                f"— При отключении доступ сохранится до конца оплаченного.\n\n"
                f"<b>Важно знать:</b> подключаясь, Ты принимаешь условия\n"
                f"ежемесячного списания.",
                parse_mode="HTML",
                reply_markup=kb.give_money
            )
    else:
        is_day = await find_dayend(tg_id)
        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)
        await message.answer(
            f"Следующее списание <b>{is_day.strftime('%d.%m.%Y')}</b>\n\n"
            f"<b>Подписка на месяц — 150₽</b>\n"
            f"— Деньги будут списываться каждый месяц.\n"
            f"— Отключить автопродление можно в любой момент в этом разделе.\n"
            f"— При отключении доступ сохранится до конца оплаченного\n\n"
            f"<b>Важно знать:</b> подключаясь, Ты принимаешь условия\n"
            f"ежемесячного списания.",
            parse_mode="HTML",
            reply_markup=kb.cancelautopay
        )


@user.message(Command('ref_programm'))
async def cmd_ref(message: Message):
    tg_id = message.from_user.id
    BOT_USERNAME = 'UpUp_VPN_bot'
    ref_link = f"https://t.me/{BOT_USERNAME}?start={tg_id}"
    escaped_link = escape_markdown(ref_link)
    await message.answer(
        f"*Реферальная программа eschalon*\n\n"
        f"За каждого приглашённого друга, оформившего подписку,\n"
        f"Твой доступ продлевается на 7 дней\.\n\n"
        f"*Реферальная ссылка:*\n`{escaped_link}`",
        disable_web_page_preview=True,
        parse_mode="MarkdownV2",
        reply_markup=kb.go_home
    )


@user.callback_query(F.data == 'probnik')
async def probnik(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(f'🎁 Бесплатный доступ\n\n'
                                     f'Попробуйте VPN бесплатно перед покупкой\n\n'
                                     f'📦 В пробный период входит:\n'
                                     f'• До 2 устройств одновременно\n'
                                     f'• Доступ ко всем серверам\n'
                                     f'• Без ограничений по трафику\n\n'
                                     f'⏳ Доступ: 3 дня\n'
                                     f'🎯 Можно активировать только один раз\n'
                                     f'⚡ Подключение занимает меньше 1 минуты\n\n'
                                     f'👇 Нажмите кнопку ниже, чтобы начать',
                                     reply_markup=kb.prob
                                     )

@user.callback_query(F.data == 'aktiviroval')
async def aktivttrail(callback: CallbackQuery):
    tg_id = callback.from_user.id
    tariff_id = 1
    sub = await find_sub(tg_id)
    await change_trial(tg_id)
    if not sub:
        await addkey(tg_id, tariff_id)
        is_day = await find_dayend(tg_id)
        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)
        await callback.answer('')
        await callback.message.edit_text(f'✅ Пробный доступ активирован\n\n'
                                         f'⏳ Действует до: {is_day.strftime('%d.%m.%Y')}\n\n'
                                         f'📊 Условия:\n'
                                         f'• 1 устройство одновременно\n'
                                         f'• Без ограничения по трафику\n'
                                         f'• Доступ ко всем доступным серверам\n\n'
                                         f'⚡ Подключение занимает меньше 1 минуты 👇',
                                         reply_markup=kb.plus_trial)
    else:
        await plus_subtime(tg_id, tariff_id)
        is_day = await find_dayend(tg_id)
        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)
        await callback.answer('')
        await callback.message.edit_text(f'✅ Пробный доступ активирован\n\n'
                                         f'⏳ Действует до: {is_day.strftime('%d.%m.%Y')}\n\n'
                                         f'📊 Условия:\n'
                                         f'• 1 устройство одновременно\n'
                                         f'• Без ограничения по трафику\n'
                                         f'• Доступ ко всем доступным серверам\n\n'
                                         f'⚡ Подключение занимает меньше 1 минуты 👇',
                                         reply_markup=kb.plus_trial)



@user.callback_query(F.data == 'period')
async def period(callback: CallbackQuery):
    tg_id = callback.from_user.id
    is_key = await find_key(tg_id)
    if not is_key:
        await callback.answer('')
        await callback.message.edit_text('*Выберите ваше устройство:*',
                                         parse_mode="MarkdownV2",
                                         reply_markup=kb.gadgets_old)
    else:
        is_day = await find_dayend(tg_id)
        now_moscow = datetime.now(tz=MOSCOW_TZ)
        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)
        if is_day > now_moscow:
            await callback.answer('')
            await callback.message.edit_text('*Выберите ваше устройство:*',
                                             parse_mode="MarkdownV2",
                                             reply_markup=kb.gadgets_old)
        else:
            await callback.answer('')
            await callback.message.edit_text('*У вас нет активной подписки*',
                                               parse_mode="MarkdownV2",
                                               reply_markup=kb.go_pay)


@user.callback_query(F.data == 'android')
async def connect_an(callback: CallbackQuery):
    user_id = callback.from_user.id
    tarif_id = await find_tarif(user_id)
    is_key = await find_key(user_id)
    if not is_key:
      await addkey(user_id, tarif_id)
    is_key = await find_key(user_id)
    await callback.answer('')
    await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                       f'<b>№1</b> - скачай приложение'
                                       f' <a href="https://play.google.com'
                                       f'/store/apps/details?id=com.v2raytun.android">v2RayTun</a>'"\n"
                                       "<b>№2</b> - Нажми на ключ доступа cнизу (начинается с vless://)\n"
                                       "<b>№3</b> - Запусти программу v2RayTun и нажми на <b>+</b>"
                                       " в правом верхнем углу\n"
                                       "<b>№4</b> -  Выбери «Импорт из буфера обмена»\n"
                                       "<b>№5</b> - Нажми круглую кнопку включения\n\n"
                                       f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                       disable_web_page_preview=True,
                                       parse_mode="HTML",
                                    reply_markup=kb.downloadand)



@user.callback_query(F.data == 'iphone')
async def connect_i(callback: CallbackQuery):
    user_id = callback.from_user.id
    tarif_id = await find_tarif(user_id)
    is_key = await find_key(user_id)
    if not is_key:
      await addkey(user_id, tarif_id)
    is_key = await find_key(user_id)
    await callback.answer('')
    await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                       f'<b>№1</b> - Cкачай приложение'
                                       f' <a href="https://apps.apple.com'
                                       f'/lt/app/v2raytun/id6476628951">v2RayTun</a>'"\n"
                                       "<b>№2</b> - Нажми на ключ доступа cнизу (начинается с vless://)\n"
                                       "<b>№3</b> - Запусти программу v2RayTun и нажми на <b>+</b>"
                                       " в правом верхнем углу\n"
                                       "<b>№4</b> -  Выбери «Импорт из буфера обмена»\n"
                                       "<b>№5</b> - Нажми круглую кнопку включения\n\n"
                                       f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                       disable_web_page_preview=True,
                                       parse_mode="HTML",
                                     reply_markup=kb.downloadiph)



@user.callback_query(F.data == 'huawei')
async def connect_hu(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    tarif_id = await find_tarif(user_id)
    if not is_key:
      await addkey(user_id, tarif_id)
    is_key = await find_key(user_id)
    await callback.answer('')
    await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                       f'<b>№1</b> - Cкачай приложение'
                                       f' <a href="https://github.com/barmaiey5553/V2RayTun-for-china-mobile'
                                       f'/releases/download/v1.0/v2RayTun_3.10.42_arm64-v8a.apk">v2RayTun</a>'"\n"
                                       "<b>№2</b> - Нажми на ключ доступа cнизу (начинается с vless://)\n"
                                       "<b>№3</b> - Запусти программу v2RayTun и нажми на <b>+</b>"
                                       " в правом верхнем углу\n"
                                       "<b>№4</b> -  Выбери «Импорт из буфера обмена»\n"
                                       "<b>№5</b> - Нажми круглую кнопку включения\n\n"
                                       f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                       disable_web_page_preview=True,
                                       parse_mode="HTML",
                                     reply_markup=kb.downloadHUA)


@user.callback_query(F.data == 'windows')
async def connect_win(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    tarif_id = await find_tarif(user_id)
    if not is_key:
      await addkey(user_id, tarif_id)
    is_key = await find_key(user_id)
    await callback.answer('')
    await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                       f'<b>№1</b> - Скачай приложение'
                                       f' <a href="https://github.com/MatsuriDayo/nekoray/releases'
                                       f'/download/4.0.1/nekoray-4.0.1-2024-12-12-windows64.zip">NekoBox</a>'"\n"
                                       "<b>№2</b> - Нажми на ключ доступа cнизу (начинается с vless://)\n"
                                       "<b>№3</b> - Разархивируй и запусти программу «NekoBox» от имени администратора\n"
                                       "<b>№4</b> - Включи режим TUN в правом веерхнем углу \n"
                                       "<b>№5</b> - Нажми правой кнопкой мыши по пустому пространству"
                                       " и выбери «Добавить профиль из буфера обмена»\n"
                                       "<b>№6</b> - Нажми правой кнопкой мыши по появившимуся профилю"
                                       " и выбери «Запустить»\n\n"
                                       f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                       disable_web_page_preview=True,
                                       parse_mode="HTML",
                                     reply_markup=kb.downloadwin)


@user.callback_query(F.data == 'macos')
async def connect_mc(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    tarif_id = await find_tarif(user_id)
    if not is_key:
      await addkey(user_id, tarif_id)
    is_key = await find_key(user_id)
    await callback.answer('')
    await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                           f'<b>№1</b> - Скачай приложение'
                                           f' <a href="https://github.com/MatsuriDayo/nekoray/releases'
                                           f'/download/4.0.1/nekoray-4.0.1-2024-12-12-windows64.zip">v2RayTun</a>'"\n"
                                           "<b>№2</b> - Нажми на ключ доступа cнизу (начинается с vless://)\n"
                                           "<b>№3</b> - Разархивируй и запусти программу «NekoBox»"
                                           " имени администратора\n"
                                           "<b>№4</b> - Включи режим TUN в правом веерхнем углу \n"
                                           "<b>№5</b> - Нажми правой кнопкой мыши по пустому пространству"
                                           " и выбери «Добавить профиль из буфера обмена»\n"
                                           "<b>№6</b> - Нажми правой кнопкой мыши по появившимуся профилю"
                                           " и выбери «Запустить»\n\n"
                                           f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                           disable_web_page_preview=True,
                                           parse_mode="HTML",
                                           reply_markup=kb.downloadwin)



@user.callback_query(F.data == 'androidtv')
async def connect_antv(callback: CallbackQuery):
    user_id = callback.from_user.id
    is_key = await find_key(user_id)
    tarif_id = await find_tarif(user_id)
    if not is_key:
      await addkey(user_id, tarif_id)
    is_key = await find_key(user_id)
    await callback.answer('')
    await callback.message.edit_text(f'<b>ИНСТРУКЦИЯ:</b>\n\n'
                                       f"<b>№1</b> - Установи пульт на свой телефон по кнопке ниже\n"
                                       "<b>№2</b> - Нажми на ключ доступа cнизу (начинается с vless://)\n"
                                       "<b>№3</b> - Установи v2RayTun на Android TV\n"
                                       "<b>№4</b> - Запусти v2RayTun и выбери пункт «ручной ввод»\n"
                                       "<b>№5</b> - Вставь скопированный ключ используя установленный пульт\n"
                                       "<b>№6</b> - Нажми <b>Ок</b>\n\n"
                                       f"<blockquote expandable><code>{html.escape(is_key)}</code></blockquote>",
                                       disable_web_page_preview=True,
                                       parse_mode="HTML",
                                     reply_markup=kb.downloadTV)



@user.callback_query(F.data == 'refka')
async def refka(callback: CallbackQuery):
    tg_id = callback.from_user.id
    BOT_USERNAME = 'UpUp_VPN_bot'
    ref_link = f"https://t.me/{BOT_USERNAME}?start={tg_id}"
    escaped_link = escape_markdown(ref_link)
    await callback.answer('')
    await callback.message.edit_text(
        f"*Реферальная программа eschalon*\n\n"
        f"За каждого приглашённого друга, оформившего подписку,\n"
        f"Твой доступ продлевается на 7 дней\.\n\n"
        f"*Реферальная ссылка:*\n`{escaped_link}`",
        parse_mode="MarkdownV2",
        reply_markup=kb.go_home
    )


@user.callback_query(F.data == 'pay')
async def sub(callback: CallbackQuery):
    tg_id = callback.from_user.id
    paymenthodid = await find_paymethod_id(tg_id)
    tarif = await find_tarif(tg_id)
    if not paymenthodid:
        is_sub = await find_sub(tg_id)
        now_moscow = datetime.now(tz=MOSCOW_TZ)
        is_day = await find_dayend(tg_id)
        if not is_sub:
            await callback.answer('')
            await callback.message.edit_text(
                '<b>Выберите тариф:</b>\n\n'
                '🔹 1 устройство\n'
                '💰 от 179₽/мес\n\n'
                '🔹 2 устройства\n'
                '💰 от 269₽/мес\n\n'
                '🔹 5 устройств\n'
                '💰 от 555₽/мес\n\n'
                'Количество устройств — это число одновременных подключений\n'
                '👇 Выберите подходящий вариант',
                parse_mode="HTML",
                reply_markup=kb.choose_duration
            )
        elif is_day < now_moscow:
            await callback.answer('')
            await callback.message.edit_text(
                '<b>Выберите тариф:</b>\n\n'
                '🔹 1 устройство\n'
                '💰 от 179₽/мес\n\n'
                '🔹 2 устройства\n'
                '💰 от 269₽/мес\n\n'
                '🔹 5 устройств\n'
                '💰 от 555₽/мес\n\n'
                'Количество устройств — это число одновременных подключений\n'
                '👇 Выберите подходящий вариант',
                parse_mode="HTML",
                reply_markup=kb.choose_duration
            )

        else:
            await callback.answer('')
            await callback.message.edit_text(
                f"<b>Текущий тариф: {tarif.name}</b>\n"
                f"<b>⏳ Действует до: {is_day.strftime('%d.%m.%Y')}</b>\n\n"
                f"Вы можете продлить подписку или выбрать другой тариф\n\n"
                f"🔹 1 устройство\n"
                f"💰 от 179₽/мес\n\n"
                f"🔹 2 устройства\n"
                f"💰 от 269₽/мес\n\n"
                f"🔹 5 устройств\n"
                f"💰 от 555₽/мес\n\n"
                f"👇 Выберите подходящий вариант",
                parse_mode="HTML",
                reply_markup=kb.choose_duration
                )
    else:
        is_day = await find_dayend(tg_id)
        if is_day.tzinfo is None:
            is_day = is_day.replace(tzinfo=MOSCOW_TZ)
        await callback.answer('')
        await callback.message.edit_text(
            f"<b>Текущий тариф: {tarif.name}</b>\n"
                f"<b>🔄 Следующее списание: {is_day.strftime('%d.%m.%Y')}</b>\n\n"
                f"Вы можете выбрать другой тариф или отключить автопродление\n\n"
                f"🔹 1 устройство\n"
                f"💰 от 179₽/мес\n\n"
                f"🔹 2 устройства\n"
                f"💰 от 269₽/мес\n\n"
                f"🔹 5 устройств\n"
                f"💰 от 555₽/мес\n\n"
                f"👇 Выберите подходящий вариант",
                parse_mode="HTML",
                reply_markup=kb.cancelautopay
                )

@user.callback_query(F.data == 'one')
async def one(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('<b>Выберите период подписки</b>\n\n'
                                     '🔹 1 месяц\n'
                                     '💰 179₽\n\n'
                                     '🔹 3 месяца\n'
                                     '💰 479₽\n\n'
                                     '🔹 6 месяцев\n'
                                     '💰 888₽\n\n'
                                     '🔹 12 месяцев\n'
                                     '💰 1699₽\n\n'
                                     '<b>🔄 Подписка продлевается автоматически раз в период</b>'
                                     'Вы можете отключить автопродление в любой момент в профиле',
                                     parse_mode="HTML",
                                     reply_markup=kb.give_money_1)

@user.callback_query(F.data == 'two')
async def one(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('</b>Выберите период подписки</b>\n\n'
                                     '🔹 1 месяц\n'
                                     '💰 269₽\n\n'
                                     '🔹 3 месяца\n'
                                     '💰 699₽\n\n'
                                     '🔹 6 месяцев\n'
                                     '💰 1399₽\n\n'
                                     '🔹 12 месяцев\n'
                                     '💰 2699₽\n\n'
                                     '<b>🔄 Подписка продлевается автоматически раз в период</b>\n'
                                     'Вы можете отключить автопродление в любой момент в профиле',
                                     parse_mode="HTML",
                                     reply_markup=kb.give_money_2)

@user.callback_query(F.data == 'five')
async def one(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text('</b>Выберите период подписки</b>\n\n'
                                     '🔹 1 месяц\n'
                                     '💰 555₽\n\n'
                                     '🔹 3 месяца\n'
                                     '💰 1489₽\n\n'
                                     '🔹 6 месяцев\n'
                                     '💰 2888₽\n\n'
                                     '🔹 12 месяцев\n'
                                     '💰 5555₽\n\n'
                                     '<b>🔄 Подписка продлевается автоматически раз в период</b>\n'
                                     'Вы можете отключить автопродление в любой момент в профиле',
                                     parse_mode="HTML",
                                     reply_markup=kb.give_money_5)


@user.callback_query(F.data == 'plsno')
async def no(callback: CallbackQuery):
    tg_id = callback.from_user.id
    await delpaymethod_id(tg_id)
    await callback.answer('')
    await callback.message.edit_text(
        'Вы успешно отменили автопродление',
        reply_markup=kb.on_main
    )


@user.callback_query(F.data.startswith('doitpls_'))
async def pay(callback: CallbackQuery):
    idd = int(callback.data.split("_")[1])
    tg_id = callback.from_user.id
    tarif = await findd_tarif(idd)
    payment_url = await create_payment(tg_id,tarif['price'],tarif['id'])
    kburl = payment_keyboard(payment_url, idd)
    message_id = callback.message.message_id
    await save_message(tg_id, message_id)
    await callback.message.edit_text(
        f"Оплатите по ссылке:\n{payment_url}",
        reply_markup=kburl
    )
