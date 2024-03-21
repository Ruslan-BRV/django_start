from django import template

register = template.Library()

@register.inclusion_tag('include/markdown_to_html_tag.html', takes_context=True)
def markdown_to_html2(context, markdown_text):
    return {'markdown_text': markdown_text.upper() + ' - это тестовый текст'}
