from django import template
from shop.models import Category, Brand
register = template.Library()


@register.simple_tag
def categories():
    return Category.objects.filter(parent=None)


@register.simple_tag
def brands():
    return Brand.objects.all()
