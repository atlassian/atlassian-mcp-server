"""Tags: ADS Tag (@atlaskit/tag 17.0.3) in gray, its default colour, for labelling things such as the apps a page
searched. CSS: tag.css."""
from .page import e


def tag(text):
    """A tag: 20px, with its text in body.small, cut with an ellipsis past 180px. An app that found nothing is a tag
    like any other, its text saying so.

        tag('Confluence')
        tag('No results from Google Drive')
    """
    return f'<span class="tag"><span class="tag__text">{e(text)}</span></span>'
