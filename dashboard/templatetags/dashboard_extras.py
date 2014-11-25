from django import template

from dashboard.models import Category, EmbeddedVisualization

register = template.Library()


@register.inclusion_tag('nav_bar.html')
def category_menu():
    menu = {}
    category_visualizations = {}

    categories = Category.objects.filter(enabled=True).order_by('name')

    menu['categories'] = categories

    for category in categories:
        category_visualizations[category] = EmbeddedVisualization.objects.filter(category=category)

    menu['category_visualizations'] = category_visualizations

    return menu


@register.inclusion_tag('footer.html')
def footer():
    pass
