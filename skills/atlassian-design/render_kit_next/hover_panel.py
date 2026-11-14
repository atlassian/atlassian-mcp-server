"""Hover panels: a button that opens a small panel of rows on hover, focus or a tap, like ✦ AI Components'
Sources popup (4921:12954). CSS: hover_panel.css, and the page script, SCRIPT.
"""
from .page import e

# Opens on hover after ADS Tooltip's 300ms and on keyboard focus, stays open over the trigger or the panel, and
# toggles on a click or a tap. Esc closes it and keeps focus on the trigger, and it closes when the pointer leaves,
# focus moves away or a tap lands elsewhere. It opens above its trigger when there's no room below, and
# left-aligned when there's no room to its left.
SCRIPT = '''
(function(){
  [].forEach.call(document.querySelectorAll('.hover-panel'),function(w){
    var b=w.querySelector('.hover-panel__trigger'),p=w.querySelector('.hover-panel__panel'),t;
    function later(f,ms){clearTimeout(t);t=setTimeout(f,ms);}
    function open(){clearTimeout(t);if(!p.hidden)return;p.hidden=false;b.setAttribute('aria-expanded','true');
      w.classList.remove('hover-panel--above','hover-panel--start');var r=p.getBoundingClientRect();
      if(r.left<0)w.classList.add('hover-panel--start');
      if(r.bottom>innerHeight&&b.getBoundingClientRect().top>r.height+8)w.classList.add('hover-panel--above');}
    function close(){clearTimeout(t);p.hidden=true;b.setAttribute('aria-expanded','false');}
    w.addEventListener('pointerenter',function(ev){if(ev.pointerType==='mouse')later(open,p.hidden?300:0);});
    w.addEventListener('pointerleave',function(ev){if(ev.pointerType==='mouse')later(close,100);});
    b.addEventListener('click',function(){if(p.hidden)open();else close();});
    b.addEventListener('focus',function(){if(b.matches(':focus-visible'))open();});
    w.addEventListener('focusout',function(ev){if(!w.contains(ev.relatedTarget))close();});
    w.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&!p.hidden){close();b.focus();}});
    document.addEventListener('pointerdown',function(ev){if(!w.contains(ev.target))close();});
  });
})();
'''


def hover_panel(trigger, label, heading, rows, id):
    """A button holding the trigger HTML, named by label, and the panel it opens below it, right-aligned, holding
    the heading, then the rows HTML. id names the panel.

        hover_panel(avatars, 'Reviewers, 5', '5 reviewers', panel_row(avatar, 'Riley Novak', 'Product lead'), 'reviewers')
    """
    return (f'<div class="hover-panel"><button class="hover-panel__trigger" type="button" aria-expanded="false" '
            f'aria-controls="{e(id)}" aria-label="{e(label)}">{trigger}</button>'
            f'<div class="hover-panel__panel" id="{e(id)}" hidden><p class="hover-panel__heading">{e(heading)}</p>'
            f'<ul class="hover-panel__rows">{rows}</ul></div></div>')


def panel_row(lead, title, *line):
    """A panel row: the lead HTML (an avatar or a logo), the title HTML at 14/20 medium, then any line items in
    12/16 subtle text, a "•" between them.

        panel_row(initials('Riley Novak'), 'Riley Novak', 'Product lead', status)
    """
    dot = '<span class="hover-panel__dot">•</span>'
    line = f'<span class="hover-panel__line">{dot.join(line)}</span>' if line else ''
    return f'<li class="hover-panel__row">{lead}<span><span class="hover-panel__title">{title}</span>{line}</span></li>'
