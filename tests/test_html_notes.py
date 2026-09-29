from html.parser import HTMLParser

from gramps_fancy_book.domain import Note
from gramps_fancy_book.renderers.html_notes import render_html_note


class _ActiveMarkupParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.attributes = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag.casefold())
        self.attributes.extend(
            (name.casefold(), value or "") for name, value in attrs
        )

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)


def test_markdown_note_html_cannot_inject_active_markup_or_javascript_links():
    note = Note(
        handle="n1",
        text=(
            "<script>alert(1)</script>\n\n"
            "<img src=x onerror=alert(1)>\n\n"
            "[dangerous](javascript:alert(1))\n\n"
            "[source](https://example.invalid/record?a=1&b=2)"
        ),
    )

    rendered = render_html_note(note)
    parser = _ActiveMarkupParser()
    parser.feed(rendered)

    assert "script" not in parser.tags
    assert "img" not in parser.tags
    assert not any(name.startswith("on") for name, _ in parser.attributes)
    assert "javascript:alert(1)" not in {
        value for name, value in parser.attributes if name == "href"
    }
    assert {
        value for name, value in parser.attributes if name == "href"
    } == {"https://example.invalid/record?a=1&b=2"}
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered
    assert "&lt;img src=x onerror=alert(1)&gt;" in rendered


def test_html_code_note_is_displayed_as_literal_text():
    note = Note(
        handle="n2",
        text='<script>alert(1)</script><img src=x onerror="alert(1)">',
        type="HtmlCode",
    )

    rendered = render_html_note(note)
    parser = _ActiveMarkupParser()
    parser.feed(rendered)

    assert "script" not in parser.tags
    assert "img" not in parser.tags
    assert not any(name.startswith("on") for name, _ in parser.attributes)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in rendered
    assert '&lt;img src=x onerror="alert(1)"&gt;' in rendered
