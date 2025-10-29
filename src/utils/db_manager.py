from src.repositories.auth.refresh_token import RefreshTokenRepository
from src.repositories.auth.user import UserRepository
from src.repositories.commerce.category import CategoryRepository
from src.repositories.commerce.customer import CustomerRepository
from src.repositories.commerce.supplier import SupplierRepository
from src.repositories.commerce.order import OrderRepository
from src.repositories.commerce.order_item import OrderItemRepository
from src.repositories.commerce.payment import PaymentRepository
from src.repositories.commerce.product import ProductRepository
from src.repositories.report.report_task import ReportTaskRepository
from src.repositories.report.report_template import ReportTemplateRepository



class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.refresh_token = RefreshTokenRepository(self.session)
        self.user = UserRepository(self.session)
        self.category = CategoryRepository(self.session)
        self.customer = CustomerRepository(self.session)
        self.supplier = SupplierRepository(self.session)
        self.order = OrderRepository(self.session)
        self.order_item = OrderItemRepository(self.session)
        self.payment = PaymentRepository(self.session)
        self.product = ProductRepository(self.session)
        self.report_task = ReportTaskRepository(self.session)
        self.report_template = ReportTemplateRepository(self.session)

        return self

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
