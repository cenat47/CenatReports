import pytest

REPORT_PAYLOAD = {
    "report_name": "daily_sales",
    "parameters": {"date_from": "2028-11-16", "date_to": "2029-11-15"},
}


@pytest.mark.asyncio
async def test_create_report_as_manager(authenticated_manager):
    resp = await authenticated_manager.post("/report/generate", json=REPORT_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data or "task_id" in data
