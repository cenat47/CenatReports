import sys
from pathlib import Path

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

fake = Faker()

NUM_CATEGORIES = 5
NUM_SUPPLIERS = 5
NUM_PRODUCTS = 20
NUM_CUSTOMERS = 10
NUM_ORDERS = 30

AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def create_categories(session):
    categories = []
    for _ in range(NUM_CATEGORIES):
        c = CategoryORM(name=fake.word()[:100].capitalize())
        session.add(c)
        categories.append(c)
    await session.commit()
    return categories


async def create_suppliers(session):
    suppliers = []
    for _ in range(NUM_SUPPLIERS):
        s = SupplierORM(name=fake.company()[:100], contact_info=fake.email()[:200])
        session.add(s)
        suppliers.append(s)
    await session.commit()
    return suppliers


async def create_products(session, categories, suppliers):
    products = []
    for _ in range(NUM_PRODUCTS):
        p = ProductORM(
            name=fake.word()[:100].capitalize(),
            price=round(random.uniform(5, 500), 2),
            category_id=random.choice(categories).id,
            supplier_id=random.choice(suppliers).id,
        )
        session.add(p)
        products.append(p)
    await session.commit()
    return products


async def create_customers(session):
    customers = []
    for _ in range(NUM_CUSTOMERS):
        c = CustomerORM(
            name=fake.name()[:100],
            email=fake.unique.email()[:100],
            phone=fake.phone_number()[:20],
            address=fake.address()[:200],
        )
        session.add(c)
        customers.append(c)
    await session.commit()
    return customers


async def create_orders(session, customers, products):
    orders = []
    for _ in range(NUM_ORDERS):
        customer = random.choice(customers)
        order_date = fake.date_between(start_date="-1y", end_date="today")
        o = OrderORM(
            customer_id=customer.id,
            order_date=order_date,
            status=random.choice(["pending", "paid", "shipped"]),
            total_amount=0,
        )
        session.add(o)
        await session.commit()

        num_items = random.randint(1, 5)
        total = 0
        for _ in range(num_items):
            product = random.choice(products)
            quantity = random.randint(1, 3)
            price = product.price
            total += price * quantity
            oi = OrderItemOrm(
                order_id=o.id, product_id=product.id, quantity=quantity, price=price
            )
            session.add(oi)
        o.total_amount = round(total, 2)
        orders.append(o)
        await session.commit()
    return orders


async def create_payments(session, orders):
    for order in orders:
        num_payments = random.randint(1, 2)
        paid = 0
        for _ in range(num_payments):
            if paid >= order.total_amount:
                break
            amount = round(random.uniform(10, order.total_amount - paid), 2)
            paid += amount
            p = PaymentORM(
                order_id=order.id,
                payment_date=datetime.now() - timedelta(days=random.randint(0, 30)),
                amount=amount,
                method=random.choice(["card", "cash", "paypal"])[:50],
            )
            session.add(p)
        await session.commit()


async def main():
    async with AsyncSessionLocal() as session:
        categories = await create_categories(session)
        suppliers = await create_suppliers(session)
        products = await create_products(session, categories, suppliers)
        customers = await create_customers(session)
        orders = await create_orders(session, customers, products)
        await create_payments(session, orders)
        print("DB seeded successfully!")


if __name__ == "__main__":
    asyncio.run(main())
