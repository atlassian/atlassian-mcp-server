"""Lozenges for status and type. Their CSS is in ads.css."""
from html import escape

TONES = {'success': 'success', 'warning': 'warning', 'danger': 'danger', 'information': 'information',
         'discovery': 'discovery', 'neutral': ''}


def lz(item):
    """A lozenge, or nothing for an empty value.

    Data: {"text": "At risk", "tone": "warning"}, or a plain string for a neutral one. The tone is one of
    success, warning, danger, information, discovery and neutral.

        lz({"text": "Blocked", "tone": "danger"})
    """
    if not item:
        return ''
    if isinstance(item, str):
        item = {'text': item}
    tone = TONES.get(item.get('tone', 'neutral'), '')
    return f'<span class="lozenge{" lozenge--" + tone if tone else ""}">{escape(str(item["text"]), quote=True)}</span>'


def lz_text(item):
    """The text of a lozenge given as a dict or a plain string.

        lz_text({"text": "At risk", "tone": "warning"})  # "At risk"
    """
    return item.get('text') if isinstance(item, dict) else item
