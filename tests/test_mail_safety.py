from api_integration.mail.sanitizers import sanitize_filename


def test_dot_components_cannot_escape_message_directory():
    assert sanitize_filename('.') == ''
    assert sanitize_filename('..') == ''
    assert sanitize_filename('../..') == ''
    assert '/' not in sanitize_filename('../../attachment.xlsx')
    assert sanitize_filename('CON.xlsx') == '_CON.xlsx'


def test_duplicate_attachment_names_stay_inside_message_folder(tmp_path, monkeypatch):
    from email.message import EmailMessage
    from api_integration.mail.imap import fetch

    message = EmailMessage()
    message['Message-ID'] = '..'
    message['From'] = 'demo@example.com'
    message['Subject'] = 'Synthetic attachments'
    message.set_content('Synthetic content')
    for content in (b'first', b'second'):
        message.add_attachment(content, maintype='application', subtype='octet-stream', filename='demo.xlsx')

    class Mailbox:
        def login(self, *args): pass
        def select(self, *args): pass
        def search(self, *args): return 'OK', [b'1']
        def fetch(self, *args): return 'OK', [(b'1', message.as_bytes())]
        def close(self): pass
        def logout(self): pass

    monkeypatch.setattr(fetch.imaplib, 'IMAP4_SSL', lambda *args: Mailbox())
    monkeypatch.setattr(fetch, 'is_trusted_email', lambda *args: True)
    monkeypatch.chdir(tmp_path)
    download = tmp_path / 'downloads'
    fetch.fetch_mail(download_dir=str(download))
    folder = download / 'empty_msgid_1'
    assert (folder / 'demo.xlsx').read_bytes() == b'first'
    assert (folder / 'demo_1.xlsx').read_bytes() == b'second'
    assert not (tmp_path / 'demo_1.xlsx').exists()


def test_exchange_message_folder_rejects_outside_junk_path(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import pytest
    from api_integration.mail.ews import fetch

    message = SimpleNamespace(message_id='synthetic-message', sender=SimpleNamespace(email_address='demo@example.com'))
    monkeypatch.setattr(fetch, 'is_trusted_email', lambda *args: False)
    with pytest.raises(ValueError, match='escapes'):
        fetch._process_single_message(message, str(tmp_path / 'downloads'), (), '../../outside')


def test_exchange_duplicate_attachments_use_same_safe_path(tmp_path, monkeypatch):
    from exchangelib import FileAttachment
    from api_integration.mail.ews.fetch import _process_attachment

    monkeypatch.chdir(tmp_path)
    folder = tmp_path / 'message'
    folder.mkdir()
    first = FileAttachment(name='demo.xlsx', content=b'first')
    second = FileAttachment(name='demo.xlsx', content=b'second')
    assert _process_attachment(first, str(folder), ()) == 1
    assert _process_attachment(second, str(folder), ()) == 1
    assert (folder / 'demo.xlsx').read_bytes() == b'first'
    assert (folder / 'demo_1.xlsx').read_bytes() == b'second'
    assert not (tmp_path / 'demo_1.xlsx').exists()
