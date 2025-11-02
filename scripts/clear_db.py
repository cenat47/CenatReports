import sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


import asyncio

from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.database import engine
from src.models.auth.user import UserORM

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
    result = await session.execute(
        delete(UserORM).where(UserORM.email == settings.ADMIN_EMAIL)
    )
    await session.commit()

    admin = UserORM(
        email=settings.ADMIN_EMAIL,
        password_hash=settings.ADMIN_PASS,
        first_name="System",
        last_name="Admin",
        role="superadmin",
        is_active=True,
        registered_at=datetime.utcnow(),
    )
    session.add(admin)
    await session.commit()
    print(f"Admin user created: {settings.ADMIN_EMAIL}")


async def main():
    async with AsyncSessionLocal() as session:
        await clear_tables(session)


if __name__ == "__main__":
    asyncio.run(main())
