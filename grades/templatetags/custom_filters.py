from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary[key] if key in dictionary else 0

register.filter('get_item', get_item)
