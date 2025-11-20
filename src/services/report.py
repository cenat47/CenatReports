import json
from schemas.report.report_task import ReportTaskAdd, Status
from src.services.base import BaseService
from src.tasks.tasks import make_report


class ReportService(BaseService):
    async def generate_report_task(
        self, user_id: int, report_name: str, parameters: dict
    ):
        report = await self.db.report_template.get_one_or_none(name=report_name)
        if report is None:
            raise ValueError(f"Report template '{report_name}' not found")
        template_id = report.id
        new_task = ReportTaskAdd(
            user_id=user_id,
            template_id=template_id,
            status=Status.pending,
            parameters=json.dumps(parameters),
        )
        created_task = await self.db.report_task.add(new_task)
        await self.db.commit()

        make_report.delay(created_task.id)
        return {"task_id": created_task.id, "status": "pending"}
