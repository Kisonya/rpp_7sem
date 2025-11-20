import asyncio
import json
import random
import time
from datetime import datetime
from pathlib import Path

CATEGORIES = ["food", "transport", "entertainment", "shopping", "health"]


async def generate_transaction():
    """Генерирует одну транзакцию"""
    await asyncio.sleep(0)  # имитация реактивного стиля
    return {
        "timestamp": datetime.now().isoformat(),
        "category": random.choice(CATEGORIES),
        "amount": round(random.uniform(50, 5000), 2)
    }


async def generate_batch(batch_size: int):
    """Генерирует пачку транзакций"""
    return [await generate_transaction() for _ in range(batch_size)]


async def save_batch(batch, batch_number):
    """Сохраняет пачку транзакций"""
    filename = Path("transactions.json")

    # если файла нет — создаём пустой массив
    if not filename.exists():
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([], f)

    # читаем существующий файл
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    # добавляем новые записи
    data.extend(batch)

    # сохраняем
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"[INFO] Сохранена пачка #{batch_number} — {len(batch)} записей")


async def main():
    n = int(input("Введите количество транзакций: "))
    batch_size = 10

    total_batches = (n + batch_size - 1) // batch_size
    batch_number = 1

    for i in range(0, n, batch_size):
        batch = await generate_batch(min(batch_size, n - i))
        await save_batch(batch, batch_number)
        batch_number += 1

    print("\nГенерация завершена. Файл: transactions.json")


if __name__ == "__main__":
    asyncio.run(main())
