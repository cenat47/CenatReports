from src.models.auth.refresh_token import RefreshTokenORM
from src.models.auth.user import UserORM
from src.models.commerce.category import CategoryORM
from src.models.commerce.customer import CustomerORM
from src.models.commerce.order import OrderORM
from src.models.commerce.order_item import OrderItemOrm
from src.models.commerce.supplier import SupplierORM
from src.models.commerce.payment import PaymentORM
from src.models.commerce.product import ProductORM
from src.models.report.report_task import ReportTaskORM
from src.models.report.report_template import ReportTemplateORM

from src.schemas.auth.refresh_token import RefreshToken
from src.schemas.auth.user import User
from src.schemas.commerce.category import Category
from src.schemas.commerce.customer import Customer
from src.schemas.commerce.order import Order
from src.schemas.commerce.order_item import OrderItem
from src.schemas.commerce.supplier import Supplier
from src.schemas.commerce.payment import Payment
from src.schemas.commerce.product import Product
from src.schemas.report.report_task import ReportTask
from src.schemas.report.report_template import ReportTemplate

from src.repositories.mapper.base import DataMapper


class RefreshTokenDataMapper(DataMapper):
    db_model = RefreshTokenORM
    schema = RefreshToken

class UserDataMapper(DataMapper):
    db_model = UserORM
    schema = User

class CategoryDataMapper(DataMapper):
    db_model = CategoryORM
    schema = Category

class CustomerDataMapper(DataMapper):
    db_model = CustomerORM
    schema = Customer

class OrderDataMapper(DataMapper):
    db_model = OrderORM
    schema = Order

class OrderItemDataMapper(DataMapper):
    db_model = OrderItemOrm
    schema = OrderItem

class SupplierDataMapper(DataMapper):
    db_model = SupplierORM
    schema = Supplier

class PaymentDataMapper(DataMapper):
    db_model = PaymentORM
    schema = Payment

class ProductDataMapper(DataMapper):
    db_model = ProductORM
    schema = Product

class ReportTemplateDataMapper(DataMapper):
    db_model = ReportTemplateORM
    schema = ReportTemplate

class ReportTaskDataMapper(DataMapper):
    db_model = ReportTaskORM
    schema = ReportTask




