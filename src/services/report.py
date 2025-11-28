from pydantic import ValidationError
from exceptions import ReportParametersValidationException
from schemas.report.report_task import ReportTaskAdd, Status
from src.services.base import BaseService
from src.tasks.tasks import make_report
from src.tasks.report import ReportService


class ReportServiceS(BaseService):
    async def generate_report_task(
        self, user_id: int, report_name: str, parameters: dict
    ):
        # 1. Проверяем, что шаблон существует
        report = await self.db.report_template.get_one_or_none(name=report_name)
        if report is None:
            raise ValueError(f"Шаблон '{report_name}' не найден")

        report_service = ReportService(self.db)
        config = report_service.report_config.get(report_name)
        if not config:
            raise ReportParametersValidationException()

        # 3. Валидируем параметры
        try:
            validated_params = config["param_model"](**parameters)
        except ValidationError:
            raise ReportParametersValidationException()
        # 4. Создаём задачу
        new_task = ReportTaskAdd(
            user_id=user_id,
            template_id=report.id,
            status=Status.pending,
            parameters=validated_params.model_dump_json(),
        )

        created_task = await self.db.report_task.add(new_task)
        await self.db.commit()

        make_report.delay(created_task.id)

        return {"task_id": created_task.id, "status": "pending"}
