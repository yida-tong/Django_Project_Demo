import django_tables2 as tables
from django.utils.html import format_html

from .models import Shipment


class ShipmentTable(tables.Table):
    id = tables.Column(verbose_name='Edit')
    pk = tables.Column(accessor="id", verbose_name="id")

    def render_id(self, value):
        return format_html('<a href="{}/update/"><i class="fa fa-edit"></i></a>', value)

    class Meta:
        model = Shipment
        order_by = ['id']
        fields = ['id', 'pk', 'TrackingNum', 'ShipDate', 'status', 'PackageWeight', 'payer', 'RecipientStreet', 'RecipientCity', 'RecipientState', 'RecipientZip', 'is_imported']
        attrs = {'class': 'table table-striped', 'style': 'display: block; overflow: auto;'}