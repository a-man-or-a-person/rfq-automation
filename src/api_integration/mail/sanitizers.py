import re
from pathlib import Path


def sanitize_filename(filename):
    """Removes illegal characters from filenames to prevent OS errors."""
    # Remove characters that are invalid in Windows/Linux filenames
    value = re.sub(r'[\\/*?:"<>|]', "", filename).strip().rstrip('. ')


    reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}
    return '_' + value if value.split('.')[0].upper() in reserved else value


def unique_attachment_path(directory, filename):
    folder = Path(directory).resolve()
    name = sanitize_filename(filename)
    if not name:
        raise ValueError('Empty attachment filename')
    candidate = folder / name
    counter = 1
    while candidate.exists():
        candidate = folder / f'{Path(name).stem}_{counter}{Path(name).suffix}'
        counter += 1
    if not candidate.resolve().is_relative_to(folder):
        raise ValueError('Attachment escapes message directory')
    return str(candidate)
