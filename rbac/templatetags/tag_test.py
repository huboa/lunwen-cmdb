import re
from django.template import Library
from django.conf import settings
register = Library()

@register.simple_tag
def test(a1,a2):
    return a1+a2