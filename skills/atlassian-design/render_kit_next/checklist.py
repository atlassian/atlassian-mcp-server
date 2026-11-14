"""Checklists: native checkboxes drawn after ADS Checkbox (@atlaskit/checkbox 19.3.1). CSS: checklist.css."""
from .links import text
from .page import texts

TICK = ('M16.3262 9.48011L15.1738 8.51984L10.75 13.8284L8.82616 11.5198L7.67383 12.4801L10.1738 15.4801C10.3163 15.6511 '
        '10.5274 15.75 10.75 15.75C10.9726 15.75 11.1837 15.6511 11.3262 15.4801L16.3262 9.48011Z')


def checklist(items):
    """A list of checkboxes, 8px apart, each labelled with a text field. Ticks aren't saved.

        checklist(['Has a site admin set an idle timeout?', 'Is the `beacon.session.activity-heartbeat` flag on?'])
    """
    box = (f'<svg class="checkbox__icon" width="24" height="24" viewBox="0 0 24 24" aria-hidden="true">'
           f'<rect x="5.5" y="5.5" width="13" height="13" rx="1.5"/><path class="checkbox__tick" d="{TICK}"/></svg>')
    return '<ul class="checklist">' + ''.join(
        f'<li><label class="checkbox"><span class="checkbox__control"><input class="checkbox__input" type="checkbox">{box}</span>'
        f'<span class="checkbox__label">{text(x)}</span></label></li>' for x in texts(items)) + '</ul>'
