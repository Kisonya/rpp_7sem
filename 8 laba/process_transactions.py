import asyncio
import json

LIMITS = {
    "food": 10000,
    "transport": 5000,
    "entertainment": 8000,
    "shopping": 15000,
    "health": 12000
}


async def load_transactions():
    """Загружает транзакции из файла"""
    await asyncio.sleep(0)
    with open("transactions.json", "r", encoding="utf-8") as f:
        return json.load(f)


async def process_transaction(transaction, result_dict):
    """Обрабатывает одну транзакцию"""
    await asyncio.sleep(0)

    cat = transaction["category"]
    amount = transaction["amount"]

    result_dict[cat] = result_dict.get(cat, 0) + amount


async def check_limits(result_dict):
    """Печатает превышение лимитов расходов"""
    print("\n=== Проверка лимитов ===")

    for category, total in result_dict.items():
        limit = LIMITS.get(category, None)
        if limit and total > limit:
            print(f"[ALERT] Категория '{category}' превысила лимит! {total:.2f} / {limit}")
        else:
            print(f"[OK] {category}: {total:.2f}")


async def main():
    transactions = await load_transactions()
    result = {}

    tasks = [process_transaction(t, result) for t in transactions]
    await asyncio.gather(*tasks)

    print("\nРезультаты по категориям:")
    for k, v in result.items():
        print(f"{k}: {v:.2f}")

    await check_limits(result)


if __name__ == "__main__":
    asyncio.run(main())
