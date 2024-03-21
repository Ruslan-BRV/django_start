from django import template

register = template.Library()

@register.simple_tag
def markdown_to_html(markdown_text: str):
    return markdown_text.upper()
