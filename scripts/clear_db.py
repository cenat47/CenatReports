import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from src.database import engine

AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def clear_tables(session):
    await session.execute(text("DELETE FROM payments"))
    await session.execute(text("DELETE FROM order_items"))
    await session.execute(text("DELETE FROM orders"))
    await session.execute(text("DELETE FROM products"))
    await session.execute(text("DELETE FROM customers"))
    await session.execute(text("DELETE FROM suppliers"))
    await session.execute(text("DELETE FROM categories"))
    await session.commit()
    print("All tables cleared successfully!")


async def main():
    async with AsyncSessionLocal() as session:
        await clear_tables(session)


if __name__ == "__main__":
    asyncio.run(main())
