import aiosmtplib
from email.message import EmailMessage
import random

from app.database.requests import save_code


async def gen_code(email):
    code = random.randint(100000, 999999)
    try:
        await send_email(email, code)
    except Exception:
        return False

    await save_code(code, email)
    return True


async def send_email(email: str, code: str):
    message = EmailMessage()
    message["From"] = "VPN Service <noreply@yourvpn.com>"
    message["To"] = email
    message["Subject"] = "Код подтверждения"

    message.set_content(
        f"""
Ваш код подтверждения:

{code}

Если это были не вы — просто проигнорируйте письмо.
"""
    )

    await aiosmtplib.send(
        message,
        hostname="smtp.yourhost.com",
        port=465,
        username="noreply@yourvpn.com",
        password="пароль",
        use_tls=True,
    )
