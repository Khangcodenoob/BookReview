"""Markdown processing utilities."""
from markdown_it import MarkdownIt
import bleach

# Configure allowed tags and attributes
ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "p", "pre", "code", "img", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "blockquote", "hr", "br", "strong", "em"
]

ALLOWED_ATTRS = {
    "a": ["href", "title", "rel", "target"],
    "img": ["src", "alt", "title", "width", "height"],
    "code": ["class"]
}

# Initialize markdown parser
md = MarkdownIt("commonmark").enable("table").enable("strikethrough").enable("linkify")


def render_markdown_safe(text: str) -> str:
    """
    Render markdown text to HTML and sanitize it.
    
    Args:
        text: Markdown text to render
        
    Returns:
        Sanitized HTML string
    """
    if not text:
        return ""
    
    html = md.render(text)
    # Sanitize HTML to prevent XSS
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=["http", "https", "mailto"],
        strip=True
    )

