from django import template

register = template.Library()

@register.filter
def has_group(user, group_name):
    """Returns True if the user is in the specified group."""
    return user.groups.filter(name=group_name).exists()
