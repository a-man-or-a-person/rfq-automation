"""Module with app-specific constants"""

from pathlib import Path
from api_integration.config import get_settings

# Загружаем валидированные настройки приложения
settings = get_settings()


def determine_project_root() -> Path:
    # Если в .env написано APP_ENV=dev
    if settings.APP_ENV == "dev":
        return Path(__file__).resolve().parent.parent.parent

    # Если APP_ENV=prod (или не задан), корнем считается папка запуска
    # Это папка, указанная в поле "Рабочая папка" (Start in) в Windows Task Scheduler
    import os

    return Path(os.getcwd()).resolve()


project_root = determine_project_root()

# Local directory with json samples for API requests
SAMPLES_DIR = f"{project_root}/samples"

# Local directory for imcoming emails, attachments and interim precessing flags
DOWNLOADS_DIR = f"{project_root}/downloads"

# Local directory for user-level json configurations
CONFIG_DIR = f"{project_root}/config"

# Trusted recipients file location
TRUSTED_RECIPIENTS_FILE = f"{CONFIG_DIR}/trusted_recipients.json"

# Lock file location - project root (safest location)
LOCK_FILE: Path = project_root / "mail_pipeline_processor.lock"


# Flag to skip calling put_rfq_supplier_group_ids
# True - skip, False - execute (should be value)
IS_SKIP_PUT_RFQ_SUPPLIER_GROUP_IDS = settings.IS_SKIP_PUT_RFQ_SUPPLIER_GROUP_IDS

# Flag to do/skip RFQ search (by title) before creation attempt
# True for production, False for testing
IS_SEARCH_EXISTING_RFQ_BEFORE_POST = settings.IS_SEARCH_EXISTING_RFQ_BEFORE_POST

# Default lot_template_id (unless brand new created first)

# None -> MUST-BE value as template_id is not know apriori
RFQ_DEFAULT_LOT_TEMPLATE_ID: int | None = None

# The subject template to search for (IMAP does a substring match)
SUBJECT_TEMPLATE = "*"

# Full mail search pattern
# IMAP search syntax. SUBJECT does a substring match. HAS_ATTACHMENT doesn't work
# IMAP_MAIL_SEARCH_TEMPLATE = (
#     f'(SUBJECT "{SUBJECT_TEMPLATE}" HEADER "Content-Type" "multipart/mixed")'
# )
# Empty string means fetch all messages (uses IMAP "ALL" search criteria)
IMAP_MAIL_SEARCH_TEMPLATE = ""

# Accepted email attachment extensions supported by openpyxl, e.g. .xlsx, .xlsm, but NOT .xls
ALLOWED_ATTACHMENT_FILE_EXTENSIONS = (".xlsx",)

# Required patterns in attachemnt file names
ALLOWED_ATTACHMENT_LOT_TEMPLATE_TERMS = ("тз",)
ALLOWED_ATTACHMENT_RFQ_TEMPLATE_TERMS = ("шаблон", "запрос", "тендер", "параметры")

# Name of the placeholder file that indicates a reply message body has been composed
REPLY_BODY_MARKER = "reply.txt"

# Name of the placeholder file that indicates a reply has been successfully sent
REPLY_SENT_MARKER = "reply_sent.txt"

# Name of the placeholder file that indicates **result** of RFQ create API call
RFQ_INFO_MARKER = "rfq_info.json"

# Name of the placeholder file that contains fields extracted from emailed **Excel attachments**
RFQ_EXCEL_MARKER = "rfq_excel.json"

# Draft RFQ link
RFQ_DRAFT_URL = "https://example.com/rfq/{rfq_id}"

# Reply email templates
SUCCESS_REPLY_TEMPLATE = (
    "Здравствуйте,<br>"
    "В ответ на Ваше письмо {subject_line} от {date}.<br><br>"
    "Мы автоматически создали RFQ: {message} <br><br>"
    "{extra_on_success}"
    "<br><br>"
    "---- Original message ----<br>{body_excerpt}<br>"
    "------------------------------------<br><br>"
    "С наилучшими пожеланиями,<br>"
    "RFQ Automation Demo<br>"
)

ERROR_REPLY_TEMPLATE = (
    "Здравствуйте,<br>"
    "В ответ на Ваше письмо {subject_line} от {date}.<br><br>"
    "Нам не удалось автоматически создать RFQ <br><br>"
    "Описание причины:<br>"
    "{message}"
    "<br><br>"
    "---- Original message ----<br>{body_excerpt}<br>"
    "------------------------------------<br><br>"
    "С наилучшими пожеланиями,<br>"
    "RFQ Automation Demo<br>"
)

PARTIAL_SUCCESS_REPLY_TEMPLATE = (
    "Здравствуйте,<br>"
    "В ответ на Ваше письмо {subject_line} от {date}.<br><br>"
    "Мы автоматически создали RFQ: {message} <br><br>"
    "{extra_on_success}"
    "<br><br>"
    "Предупреждение:<br>"
    "{warning}"
    "<br><br>"
    "---- Original message ----<br>{body_excerpt}<br>"
    "------------------------------------<br><br>"
    "С наилучшими пожеланиями,<br>"
    "RFQ Automation Demo<br>"
)

# Possible mapping of Excel field name "Наим поля в UI"
# (from Шаблон запроса создания тендера v1.3/TENDER)
# to RfqCreateRequest properties
EXCEL_TO_RFQ_MAPPING = {
    # Core Identification & Text
    "Название": "title",
    # "Площадка": "name_for_human", # skip
    # "Направление": "name_for_human", # skip
    "Информация для поставщика услуг": "requirements",
    # Dates & Timelines
    "Дата и время окончания": "finish_datetime",
    # "Дата публикации": "published_at",
    "Срок действия ТКП от": "contract_start_date",
    "Срок действия ТКП до": "contract_end_date",
    # Access & Participants
    "Прямой доступ": "participant_access_type",
    "Пригласить поставщиков": "supplier_group_ids",
    "Полный доступ": "user_access",
    "Отправлять ссылку-приглашение по email": "is_invite_link_enabled",
    "Контактное лицо": "contact_ids",
    # Transport & Lots
    "Вид транспорта": "transport_type_ids",
    "Объем запроса предложений": "freight_spend_of_event",
    # Visibility & Traffic Light Settings
    "Показывать лучшую цену": "show_best_price",
    # "Лучшая цена": "zzz", # skip комбинация {type_view = 1, show_best_price (true/false)}
    "Светофор на основе": "traffic_light_type",
    "Показывать светофор на основе цены": "traffic_light_price_type",
    "Зеленый сигнал светофора от": "price_green_finish_percent",  # lower bound only
    "Желтый сигнал светофора от": "price_yellow_finish_percent",  # lower bound only
    # "Красный сигнал светофора от": "", # unused
    # Prolongation & Rules
    "Автоматическая пролонгация": "prolongacia",
    # "Время пролонгации": "max_date_prolongacia", # skip
    "Обратная связь для поставщиков": "type_view",
    "Повышение цен поставщиками": "is_ban_on_price_increases_on_this_tour",
}


# Mappings of excel RFQ template values "Значение по умолчанию"/"Значение" to 7rights API IDs
EXCEL_TO_RFQ_VALUES_MAPPING = {'is_invite_link_enabled': {'Да': True, 'да': True, 'Нет': False, 'нет': False}, 'transport_type_ids': {'Авто, Полная FTL': [1]}, 'participant_access_type': {'Да': 0, 'да': 0, 'Нет': 1, 'нет': 1}, 'contact_ids': {'Demo contact': [1001]}, 'user_access': {'Demo organizer': [{'user_id': 1001, 'access_type': 1}]}, 'supplier_group_ids': {'Demo suppliers': [2001]}, 'type_view': {'Запрос данных, без обратной связи': 0, 'Обратная связь в виде числового рейтинга': 1, 'Обратная связь в виде светофора': 2, 'Обратная связь в виде числового рейтинга от наибольшей цены': 3}, 'traffic_light_type': {'светофор по целевому тарифу': 1, 'светофору по рейтингу': 0}, 'traffic_light_price_type': {'Целевая цена': 2, 'Базовая цена': 1, 'Лучшая цена': 0}, 'show_best_price': {'Не показывать лучшую цену': False, 'Отобразить лучшую цену': True}, 'prolongacia': {'Запрещено': False, 'Разрешено, при переходе из красной/желтой зоны в зеленую': True, 'Разрешено, при выходе из красной в желтую/зеленую зону': True}, 'is_ban_on_price_increases_on_this_tour': {'Разрешено': False, 'Запрещено': True, 'Запрещено понижать': False}}

# Hardcoded mappings from RfqCreateRequest properties to constant values
RFQ_TO_DEFAULTS_MAPPING = {
    "access_type": "groups",  # paired with supplier_group_ids
    "freight_spend_currency_id": 1,  # Валюта RUB: freight_spend_currency_id: 1 идет вместе с freight_spend_of_event
    # "is_for_all": False,  # optional, тендер создаётся как черновик без приглашённых поставщиков
}

