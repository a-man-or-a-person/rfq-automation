"""Run the real workbook validation/mapping code on generated inputs, without network I/O."""
import argparse
import json
import os
from pathlib import Path

DEMO_ENV = {
    'RFQ_DEMO': '1', 'LIVE_INTEGRATIONS_ENABLED': 'false',
    'MAILBOX_NAME': 'demo@example.com', 'MAILBOX_APP_PASSWORD': 'demo-only',
    'SEVEN_RIGHTS_API_BASE_URL': 'https://example.com/',
    'SEVEN_RIGHTS_API_VERSION': 'api/v1/', 'SEVEN_RIGHTS_API_KEY': 'demo-only',
    'SEVEN_RIGHTS_API_AWAIT_TIMEOUT': '1', 'APP_ENV': 'dev',
    'EXCHANGE_USERNAME': 'DEMO\\demo', 'EXCHANGE_PASSWORD': 'demo-only',
    'EXCHANGE_SERVER': 'mail.example.com', 'PRIMARY_SMTP_ADDRESS': 'demo@example.com',
}


def run_demo(output: Path) -> dict:
    os.environ.update(DEMO_ENV)
    from api_integration.config import get_settings
    get_settings.cache_clear()
    from openpyxl import Workbook
    from api_integration.constants import EXCEL_TO_RFQ_MAPPING
    from api_integration.excel.excel_pipeline import process_attachments
    from api_integration.sevenrights.api.schemas.api_requests import RfqCreateRequest

    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise FileExistsError('Choose an empty output directory; existing files will not be overwritten')
    values = {
        'title': 'SYNTHETIC — regional transport sourcing',
        'finish_datetime': '2027-01-31T12:00:00',
        'user_access': 'Demo organizer', 'contact_ids': 'Demo contact',
        'supplier_group_ids': 'Demo suppliers',
    }
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'TENDER'
    sheet.append(['Field', 'Fallback', 'Value'])
    for label, field in EXCEL_TO_RFQ_MAPPING.items():
        if field in values:
            sheet.append([label, None, values[field]])
    workbook.save(output / 'synthetic_параметры.xlsx')
    workbook = Workbook()
    workbook.active.title = 'Матрица ТЗ_РФ'
    workbook.active.append(['Synthetic lot', 'Quantity'])
    workbook.active.append(['Route A → B', 10])
    workbook.save(output / 'synthetic_тз.xlsx')
    result = process_attachments(output)
    if result['error']:
        raise ValueError(result['error'])
    payload = RfqCreateRequest.model_validate(result['rfq_template']).model_dump(mode='json', exclude_none=True)
    destination = output / 'rfq-preview.json'
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('demo-output'))
    args = parser.parse_args()
    run_demo(args.output)
    print(f'Validated synthetic RFQ preview: {args.output / "rfq-preview.json"}. No mail sent; no API called.')


if __name__ == '__main__':
    main()
