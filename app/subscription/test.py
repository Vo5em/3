import asyncio
import json

from service import build_subscription


async def main():

    result = await build_subscription(
        "2fde387b-1cda-46"
    )

    with open(
        "test_output.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("Готово! JSON сохранён в test_output.json")


if __name__ == "__main__":
    asyncio.run(main())