from django import template
from data_warehouse.models import Payer
register = template.Library()


@register.inclusion_tag('mysite/sidebar.html')
def home_sidebar(request):
    return {'request': request, 'payer_num': Payer.objects.count()}


@register.inclusion_tag('mysite/err_msg.html')
def err_msg(messages):
    return {'messages': messages}