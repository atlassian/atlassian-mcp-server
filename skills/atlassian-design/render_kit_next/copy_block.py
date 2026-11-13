"""Copy blocks: text in a quote block with a Copy button after ADS Button (@atlaskit/button 25.6.1) in its default
appearance. CSS: copy_block.css, and the page script, SCRIPT.
"""
from .glyphs import glyph
from .page import e

# Copies the quote's text and says "Copied" for 1.5s. If the clipboard is blocked or missing, it selects the
# quote's text instead, so it can be copied by hand, and says "Text selected".
SCRIPT = '''
(function(){
  [].forEach.call(document.querySelectorAll('.copy-block'),function(w){
    var b=w.querySelector('.copy-block__button'),q=w.querySelector('.copy-block__text'),l=b.querySelector('.copy-block__label'),o=l.textContent,t;
    function say(s){l.textContent=s;clearTimeout(t);t=setTimeout(function(){l.textContent=o;},1500);}
    function select(){var r=document.createRange();r.selectNodeContents(q);var s=getSelection();s.removeAllRanges();s.addRange(r);say('Text selected');}
    b.addEventListener('click',function(){
      if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(q.textContent).then(function(){say('Copied');},select);else select();});
  });
})();
'''


def copy_block(text):
    """The text in a quote block, then 12px below it a Copy button with the copy glyph. The button says "Copied"
    once it has copied, and if the clipboard is blocked it selects the text instead.

        copy_block('Thanks for the details. Beacon signs people out after 30 minutes with no activity.')
    """
    return (f'<div class="copy-block"><blockquote class="copy-block__text">{e(text)}</blockquote>'
            f'<button class="copy-block__button" type="button">{glyph("copy")}<span class="copy-block__label" aria-live="polite">Copy</span></button></div>')
