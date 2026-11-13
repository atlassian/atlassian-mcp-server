"""The skill tag: ✦ AI Components' Skill Tag in its default state and Neutral colour. CSS: skill_tag.css."""
from .page import e

# Paths from the Figma parts (8046:946), in an 8 by 20 box each: the start cap with the slash over its edge,
# and the end cap turned round.
START = 'M5.5724 1.4253C5.8262 0.5793 6.6049 0 7.4881 0H8V20H2.6881C1.3484 20 .3874 18.7085 .7724 17.4253Z'
SLASH = 'M5.5724 1.4253C5.8262 0.5793 6.6049 0 7.4881 0H8L2 20C1.0032 20 .2883 19.0391 .5747 18.0843Z'
END = 'M2.5747 18.0844C2.2336 19.2214 1.1871 20 0 20V0H3.9679C5.9775 0 7.4188 1.9372 6.8414 3.862Z'


def skill_tag(slug):
    """The skill's name after a slash, on a neutral tag 20px tall. It isn't a link or a button.

        skill_tag('how-it-works')
    """
    cap = '<svg class="skill-tag__cap" width="8" height="20" viewBox="0 0 8 20" aria-hidden="true">'
    return (f'<span class="skill-tag">{cap}<path d="{START}"/><path class="skill-tag__slash" d="{SLASH}"/></svg>'
            f'<span class="skill-tag__name">{e(slug)}</span>{cap}<path d="{END}"/></svg></span>')
