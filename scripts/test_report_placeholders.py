"""Run with python3 -B scripts/test_report_placeholders.py."""
import importlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills' / 'atlassian-design'))


def main():
    for name in ('render_kit', 'render_kit_next'):
        unfilled = importlib.import_module(name).unfilled
        assert unfilled('<p>Missing {2}, {1}, and {2}</p>') == ['{1}', '{2}']
        for tag in ('script', 'style', 'SCRIPT', 'STYLE', 'sCrIpT', 'sTyLe'):
            html = f'<{tag} type="text/plain">\n{{3}}\n</{tag}> <p>{{1}}</p>'
            assert unfilled(html) == ['{1}'], (name, tag)
            assert unfilled(f'<{tag}>{{2}}</{tag}>') == [], (name, tag)
        assert unfilled('<p>&lt;script&gt;{4}&lt;/script&gt;</p>') == ['{4}']
    print('Placeholder checks pass for both report kits.')


if __name__ == '__main__':
    main()
