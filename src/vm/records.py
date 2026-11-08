# -*- coding: utf-8 -*-
"""
Records (ದಾಖಲೆ) — maps from field names to values.

Every mashable source returns records, or lists of records, that share the
standard field names below. Field names are Kannada; the English aliases are
accepted anywhere a field name is.

Words:
    get      ಪಡೆ      ( rec field -- value )      on a list: that field from every record
    set      ಇಡು      ( rec field value -- rec )  returns a new record
    keys     ಕೀಲಿಗಳು   ( rec -- list )
    values   ಮೌಲ್ಯಗಳು  ( rec -- list )
    sort-by  ಅನುಸಾರ    ( list field -- list )     ascending; use reverse for newest-first

Genitive field access lives in the VM: ಸುದ್ದಿಗಳ ಶೀರ್ಷಿಕೆ = "the news items' title".
"""

# Standard fields shared by all sources (see docs/mashables.md §4).
FIELD_ALIASES = {
    'title': 'ಶೀರ್ಷಿಕೆ',
    'summary': 'ಸಾರಾಂಶ',
    'link': 'ಕೊಂಡಿ',
    'source': 'ಮೂಲ',
    'time': 'ಸಮಯ',
    'place': 'ಸ್ಥಳ',
    'lat': 'ಅಕ್ಷಾಂಶ',
    'lon': 'ರೇಖಾಂಶ',
    'image': 'ಚಿತ್ರ',
    'temperature': 'ತಾಪಮಾನ',
    'rain': 'ಮಳೆ',
    'wind': 'ಗಾಳಿ',
    'condition': 'ಸ್ಥಿತಿ',
    'section': 'ವಿಭಾಗ',
}


def _error(msg):
    from .vm import KapilaError  # late import: vm imports this module
    return KapilaError(msg)


def is_record(value) -> bool:
    return isinstance(value, dict)


def is_record_list(value) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(v, dict) for v in value)


def _resolve(rec: dict, field: str):
    """Return the key actually present in rec for field (handling aliases), or None."""
    if field in rec:
        return field
    alias = FIELD_ALIASES.get(field)
    if alias is not None and alias in rec:
        return alias
    return None


def has_field(value, field) -> bool:
    if not isinstance(field, str):
        return False
    if is_record(value):
        return _resolve(value, field) is not None
    if is_record_list(value):
        return _resolve(value[0], field) is not None
    return False


def get_field(value, field):
    """Field of a record, or that field from every record in a list."""
    if is_record(value):
        key = _resolve(value, field)
        if key is None:
            fields = ', '.join(map(str, value.keys())) or '—'
            raise _error(f"ಕ್ಷೇತ್ರ ಇಲ್ಲ / no such field: {field}  (ಇರುವವು / available: {fields})")
        return value[key]
    if isinstance(value, list):
        if not value:
            return []
        return [get_field(v, field) for v in value]
    raise _error(f"ದಾಖಲೆ ಅಲ್ಲ / not a record: {format_value(value)}")


def builtin_get(vm):
    """( rec field -- value ) Get a field; on a list of records, from each."""
    field = vm.pop()
    rec = vm.pop()
    vm.push(get_field(rec, field))


def builtin_set(vm):
    """( rec field value -- rec ) Return a copy of rec with field set."""
    value = vm.pop()
    field = vm.pop()
    rec = vm.pop()
    if not is_record(rec):
        raise _error(f"ದಾಖಲೆ ಅಲ್ಲ / not a record: {format_value(rec)}")
    new = dict(rec)
    new[_resolve(rec, field) or field] = value
    vm.push(new)


def builtin_keys(vm):
    """( rec -- list ) Field names."""
    rec = vm.pop()
    if not is_record(rec):
        raise _error(f"ದಾಖಲೆ ಅಲ್ಲ / not a record: {format_value(rec)}")
    vm.push(list(rec.keys()))


def builtin_values(vm):
    """( rec -- list ) Field values."""
    rec = vm.pop()
    if not is_record(rec):
        raise _error(f"ದಾಖಲೆ ಅಲ್ಲ / not a record: {format_value(rec)}")
    vm.push(list(rec.values()))


def builtin_sort_by(vm):
    """( list field -- list ) Sort records by a field, ascending. Missing values go last."""
    field = vm.pop()
    items = vm.pop()
    if not isinstance(items, list):
        raise _error(f"ಪಟ್ಟಿ ಅಲ್ಲ / not a list: {format_value(items)}")

    def key(rec):
        k = _resolve(rec, field) if isinstance(rec, dict) else None
        v = rec.get(k) if k is not None else None
        # (missing?, type group, value) keeps mixed types from crashing the sort
        if v is None:
            return (1, 0, '')
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return (0, 0, v)
        return (0, 1, str(v))

    vm.push(sorted(items, key=key))


# --- Display -----------------------------------------------------------------

def format_value(value, indent: str = '') -> str:
    """Readable text for records and lists of records; str() for everything else."""
    if is_record(value):
        return '\n'.join(f"{indent}{k}: {_short(v)}" for k, v in value.items())
    if is_record_list(value):
        return '\n\n'.join(format_value(r, indent) for r in value)
    if isinstance(value, list) and value and all(isinstance(v, str) for v in value):
        # headlines, place names: one per line, not Python's ['…', '…']
        return '\n'.join(f"{indent}{v}" for v in value)
    return str(value)


def _short(v) -> str:
    if isinstance(v, dict):
        return '{' + ', '.join(f"{k}: {_short(x)}" for k, x in v.items()) + '}'
    if isinstance(v, float):
        return f"{v:g}"
    return str(v)


RECORD_BUILTINS = {
    'get': builtin_get,
    'set': builtin_set,
    'keys': builtin_keys,
    'values': builtin_values,
    'sort-by': builtin_sort_by,
}
