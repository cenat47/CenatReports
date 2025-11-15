import sys
from pathlib import Path

from src.models.report.report_template import ReportTemplateORM

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.database import engine
from src.models.commerce.category import CategoryORM
from src.models.commerce.customer import CustomerORM
from src.models.commerce.order import OrderORM
from src.models.commerce.order_item import OrderItemOrm
from src.models.commerce.payment import PaymentORM
from src.models.commerce.product import ProductORM
from src.models.commerce.supplier import SupplierORM

fake = Faker("ru_RU")

# Количество данных
NUM_CATEGORIES = 10
NUM_SUPPLIERS = 15
NUM_PRODUCTS = 80
NUM_CUSTOMERS = 60
NUM_ORDERS = 200

AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# --------------------------------------------
# Категории и товары
# --------------------------------------------

CATEGORY_LIST = [
    "Бытовая техника",
    "Смартфоны",
    "Компьютеры",
    "Одежда",
    "Обувь",
    "Игрушки",
    "Продукты питания",
    "Строительство и ремонт",
    "Книги",
    "Спорттовары",
]

PRODUCTS_BY_CATEGORY = {
    "Бытовая техника": [
        "Холодильник",
        "Пылесос",
        "Микроволновая печь",
        "Утюг",
        "Стиральная машина",
    ],
    "Смартфоны": [
        "Xiaomi Redmi",
        "iPhone",
        "Samsung Galaxy",
        "Honor View",
        "Realme Pro",
    ],
    "Компьютеры": ["Ноутбук", "Монитор", "Клавиатура", "Мышь", "SSD диск"],
    "Одежда": ["Куртка", "Джинсы", "Кофта", "Футболка", "Рубашка"],
    "Обувь": ["Кроссовки", "Ботинки", "Туфли", "Сандалии"],
    "Игрушки": ["Конструктор", "Кукла", "Мягкая игрушка", "Машинка"],
    "Продукты питания": ["Хлеб", "Молоко", "Йогурт", "Колбаса", "Сыр"],
    "Строительство и ремонт": [
        "Гипсокартон",
        "Шуруповерт",
        "Молоток",
        "Краска",
        "Кисть",
    ],
    "Книги": ["Роман", "Учебник", "Боевик", "Фэнтези", "Комикс"],
    "Спорттовары": ["Гантели", "Коврик для йоги", "Мяч", "Тренажёр"],
}

# --------------------------------------------
# Дата последних 2 лет
# --------------------------------------------


def random_date_in_last_2_years():
    return fake.date_time_between(start_date="-2y", end_date="now")


# --------------------------------------------
# Создание категорий
# --------------------------------------------


async def create_categories(session):
    categories = []
    for name in CATEGORY_LIST:
        c = CategoryORM(name=name)
        session.add(c)
        categories.append(c)
    await session.commit()
    return categories


# --------------------------------------------
# Создание поставщиков
# --------------------------------------------


async def create_suppliers(session):
    suppliers = []
    for _ in range(NUM_SUPPLIERS):
        s = SupplierORM(name=fake.company()[:100], contact_info=fake.email())
        session.add(s)
        suppliers.append(s)
    await session.commit()
    return suppliers


# --------------------------------------------
# Создание товаров
# --------------------------------------------


async def create_products(session, categories, suppliers):
    products = []
    for category in categories:
        names = PRODUCTS_BY_CATEGORY.get(category.name, [])
        for _ in range(random.randint(5, 12)):
            name = random.choice(names)

            p = ProductORM(
                name=name,
                price=round(random.uniform(100, 50000), 2),
                category_id=category.id,
                supplier_id=random.choice(suppliers).id,
            )
            session.add(p)
            products.append(p)

    await session.commit()
    return products


# --------------------------------------------
# Создание клиентов
# --------------------------------------------


async def create_customers(session):
    customers = []
    for _ in range(NUM_CUSTOMERS):
        c = CustomerORM(
            name=fake.name(),
            email=fake.unique.email(),
            phone=fake.phone_number(),
            address=fake.address(),
        )
        session.add(c)
        customers.append(c)

    await session.commit()
    return customers


# --------------------------------------------
# Создание заказов
# --------------------------------------------


async def create_orders(session, customers, products):
    orders = []

    for _ in range(NUM_ORDERS):
        customer = random.choice(customers)
        order_date = random_date_in_last_2_years()

        status = random.choice(["pending", "paid", "shipped"])

        o = OrderORM(
            customer_id=customer.id,
            order_date=order_date,
            status=status,
            total_amount=0,
        )

        session.add(o)
        await session.commit()

        num_items = random.randint(1, 6)
        total = 0

        for _ in range(num_items):
            product = random.choice(products)
            qty = random.randint(1, 4)
            price = product.price

            total += qty * price

            session.add(
                OrderItemOrm(
                    order_id=o.id, product_id=product.id, quantity=qty, price=price
                )
            )

        o.total_amount = round(total, 2)
        orders.append(o)

        await session.commit()

    return orders


# --------------------------------------------
# Создание платежей
# --------------------------------------------


async def create_payments(session, orders):
    for order in orders:
        # pending → иногда без платежей
        if order.status == "pending" and random.random() < 0.5:
            continue

        total_paid = 0
        num_payments = random.randint(1, 2)

        for _ in range(num_payments):
            if total_paid >= order.total_amount:
                break

            amount = round(
                random.uniform(
                    order.total_amount * 0.2, order.total_amount - total_paid
                ),
                2,
            )

            payment_date = order.order_date + timedelta(days=random.randint(1, 90))

            # платеж не может быть в будущем
            payment_date = min(payment_date, datetime.now())

            session.add(
                PaymentORM(
                    order_id=order.id,
                    payment_date=payment_date,
                    amount=amount,
                    method=random.choice(["card", "cash", "paypal"]),
                )
            )

            total_paid += amount

        await session.commit()


# --------------------------------------------
# Создание шаблонов отчетов
# --------------------------------------------


async def create_report_templates(session):
    # Создаем шаблон отчета daily_sales
    template = ReportTemplateORM(
        name="daily_sales",
        description="Ежедневный отчет по продажам. Показывает общую выручку, средний чек, количество заказов и другие метрики по дням. Пользователь вводит начальную и конечную даты для анализа.",
        allowed_roles="manager",
    )
    session.add(template)
    await session.commit()
    return [template]


# --------------------------------------------
# MAIN
# --------------------------------------------


async def main():
    async with AsyncSessionLocal() as session:
        categories = await create_categories(session)
        suppliers = await create_suppliers(session)
        products = await create_products(session, categories, suppliers)
        customers = await create_customers(session)
        orders = await create_orders(session, customers, products)
        await create_payments(session, orders)
        await create_report_templates(session)

        print("✅ База данных успешно заполнена!")


if __name__ == "__main__":
    asyncio.run(main())
