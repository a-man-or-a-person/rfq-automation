import logging
from typing import Any, Union
from pathlib import Path
from openpyxl import load_workbook

from api_integration.constants import RFQ_DEFAULT_LOT_TEMPLATE_ID

logger = logging.getLogger(__name__)


def read_lot_excel(
    path: Union[str, Path], sheet_name: str = "Матрица ТЗ_РФ"
) -> dict[str, Any]:
    """
    Reads lot template Excel file.
    On success returns {"lot_template_id": RFQ_DEFAULT_LOT_TEMPLATE_ID}.
    On failure returns {"error": "..."}.
    """
    try:
        wb = load_workbook(path, data_only=True)
        if sheet_name not in wb.sheetnames:
            msg = f"Sheet '{sheet_name}' not found in {path}. Available sheets: {wb.sheetnames}"
            logger.info(msg)
            return {"error": msg}
        # TODO: add data validation logic
        return {
            "lot_template_id": RFQ_DEFAULT_LOT_TEMPLATE_ID,
            "path": str(path),
        }
    except Exception as exc:
        return {"error": str(exc)}





