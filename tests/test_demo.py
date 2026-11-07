import socket

from openpyxl import load_workbook


def test_demo_validates_real_workbooks_without_network(tmp_path, monkeypatch):
    def reject_network(*args, **kwargs):
        raise AssertionError('Network access attempted by offline demo')
    monkeypatch.setattr(socket.socket, 'connect', reject_network)
    from api_integration.demo import run_demo
    payload = run_demo(tmp_path)
    assert payload['title'].startswith('SYNTHETIC')
    assert payload['contact_ids'] == [1001]
    assert payload['user_access'] == [{'user_id': 1001, 'access_type': 1}]
    assert (tmp_path / 'rfq-preview.json').is_file()
    assert 'TENDER' in load_workbook(tmp_path / 'synthetic_параметры.xlsx').sheetnames
    import pytest
    with pytest.raises(FileExistsError):
        run_demo(tmp_path)


def test_live_pipeline_requires_explicit_opt_in(monkeypatch):
    import pytest
    from api_integration.config import get_settings
    monkeypatch.setenv('LIVE_INTEGRATIONS_ENABLED', 'false')
    get_settings.cache_clear()
    from api_integration.pipeline import run_pipeline
    with pytest.raises(RuntimeError, match='Live integrations are disabled'):
        run_pipeline(dry_run=True)
