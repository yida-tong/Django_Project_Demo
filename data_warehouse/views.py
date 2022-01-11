import io
import csv
import requests
import datetime
import decimal
import random
import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, StreamingHttpResponse
from django.contrib import messages
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from django_tables2 import RequestConfig

from .models import *
from .forms import SearchShipmentForm
from .tables import ShipmentTable


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def index(request):
    context_dict = {'payers_num': Payer.objects.count(),
                    'step1': True
                    }
    return render(request, 'data_warehouse/dashboard.html', context_dict)


def csv_downloader(request):
    if request.method == 'GET' and len(request.GET) > 0:
        if request.GET['action'] == 'payers':
            url = 'https://www.dropbox.com/s/ossuev7cylglm8n/payer.csv?raw=1'
            file_name = 'payers.csv'
        elif request.GET['action'] == 'shipments':
            url = 'https://www.dropbox.com/s/0tfzh78v5dady1l/shipments.csv?raw=1'
            file_name = 'shipments.csv'
        else:
            return HttpResponseBadRequest()
        file = requests.get(url)
        if file.status_code == requests.codes.ok:
            response = HttpResponse(file.content, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(file_name)
            return response
        else:
            return HttpResponseNotFound()
    else:
        return HttpResponseBadRequest()


def csv_uploader(request):
    context_dict = {'step2': True}
    if request.method == 'POST' and request.POST['action'] == 'upload':
        payer_file = request.FILES['payers_csv']
        shipment_file = request.FILES['shipment_csv']
        if not payer_file.name.endswith('.csv') or not shipment_file.name.endswith('.csv'):
            messages.error(request, 'Not a csv file')
            return render(request, 'data_warehouse/dashboard.html', context_dict)
        if payer_file.multiple_chunks() or shipment_file.multiple_chunks():
            messages.error(request, 'File size too big (%.2f MB, %.2f MB)' % (payer_file.size / (1000 * 1000), shipment_file.size / (1000 * 1000)))
            return render(request, 'data_warehouse/dashboard.html', context_dict)

        text = io.StringIO(payer_file.read().decode('utf-8'))
        bulk_list = []
        for line in csv.reader(text):
            if line:
                bulk_dict = {
                    'first_name': line[0],
                    'last_name': line[1],
                    'dob': datetime.datetime.strptime(line[2], '%Y-%m-%d').date(),
                    'street': line[3],
                    'city': line[4],
                    'state': line[5],
                    'zip': line[6],
                    'phone': line[7],
                    'email': line[8]
                }
                bulk_list.append(Payer(**bulk_dict))
        if bulk_list:
            Payer.objects.bulk_create(bulk_list)
            pks = list(Payer.objects.all())
            text1 = io.StringIO(shipment_file.read().decode('utf-8'))
            bulk_list1 = []
            for line in csv.reader(text1):
                if line:
                    bulk_dict1 = {
                        'TrackingNum': line[0],
                        'ShipDate': datetime.datetime.strptime(line[1], '%Y-%m-%d').date(),
                        'status': line[2],
                        'delivery_date': datetime.datetime.strptime(line[3], '%Y-%m-%d').date() if line[3] else None,
                        'service_type': line[4],
                        'PackageWeight': decimal.Decimal(line[5]),
                        'ShipperStreet': line[6],
                        'ShipperCity': line[7],
                        'ShipperState': line[8],
                        'ShipperZip': line[9],
                        'RecipientStreet': line[10],
                        'RecipientCity': line[11],
                        'RecipientState': line[12],
                        'RecipientZip': line[13],
                        'payer': random.choice(pks)
                    }
                    bulk_list1.append(Shipment(**bulk_dict1))
            if bulk_list1:
                Shipment.objects.bulk_create(bulk_list1)
                messages.success(request, 'Data is added')
            else:
                messages.warning(request, 'No data is read')
        else:
            messages.warning(request, 'No data is read')
        return render(request, 'data_warehouse/dashboard.html', context_dict)
    else:
        return HttpResponseBadRequest()


def reset(request):
    context_dict = {'reset': True}
    if request.method == 'POST' and request.POST['action'] == 'reset':
        Payer.objects.all().delete()
        Shipment.objects.all().delete()
        messages.success(request, 'Reset done')
        return render(request, 'data_warehouse/dashboard.html', context_dict)
    else:
        return HttpResponseBadRequest()


def shipment_import(request):
    if request.is_ajax() and request.method == 'POST':
        pg_filter = {'is_imported': False}
        for k, v in request.POST.items():
            if k == 'submit':
                continue

            if k == 'fromShipDate':
                if v:
                    pg_filter['ShipDate__gte'] = datetime.datetime.strptime(v, '%Y-%m-%d').date()
                continue

            if k == 'toShipDate':
                if v:
                    pg_filter['ShipDate__lte'] = datetime.datetime.strptime(v, '%Y-%m-%d').date()
                continue

            v = json.loads(v)
            if k == 'payer':
                if v:
                    pg_filter[k + '__id__in'] = map(int, v)
                continue

            if v or v is False:
                pg_filter[k + '__in'] = v
        print(pg_filter)
        queryset = Shipment.objects.select_related('Payer').filter(**pg_filter)
        if request.POST['submit'] == 'true':
            return JsonResponse({'total': 'successful submit!'}, safe=False)
        else:
            total = queryset.count()
            return JsonResponse({'total': total}, safe=False)
    else:
        queryset = Shipment.objects.select_related('Payer').filter(is_imported=False)
        context_dict = {
            'payerOption': json.dumps(list(queryset.distinct('payer__id').values(name=Concat(F('payer__first_name'), Value(' '), F('payer__last_name'), output_field=CharField()), ids=F('payer__id')))),
            'serviceOption': json.dumps(list(queryset.distinct('service_type').values_list('service_type', flat=True))),
            'statusOption': json.dumps(list(queryset.distinct('status').values_list('status', flat=True))),
            'shipperCityOption': json.dumps(list(queryset.distinct('ShipperCity').values_list('ShipperCity', flat=True))),
            'shipperStateOption': json.dumps(list(queryset.distinct('ShipperState').values_list('ShipperState', flat=True))),
            'shipperZipOption': json.dumps(list(queryset.distinct('ShipperZip').values_list('ShipperZip', flat=True))),
            'recipientCityOption': json.dumps(list(queryset.distinct('RecipientCity').values_list('RecipientCity', flat=True))),
            'recipientStateOption': json.dumps(list(queryset.distinct('RecipientState').values_list('RecipientState', flat=True))),
            'recipientZipOption': json.dumps(list(queryset.distinct('RecipientZip').values_list('RecipientZip', flat=True)))
        }
    return render(request, 'data_warehouse/import_shipments.html', context_dict)


#
# def shipment_listing(request):
#     return
#
#

#
# def apply_surcharge(request):
#     return



# def unit_price_management(request):
#     return
#
#


def video_player(request):
    context_dict = {}
    return render(request, 'data_warehouse/video_tester.html', context_dict)


def shipment_search(request):
    context_dic = {
        'form': SearchShipmentForm,
        'table': None,
    }
    if request.method == 'GET':
        if request.GET.get('action'):
            if request.GET['action'] == 'search' or request.GET['action'] == 'download-as-csv':
                form = SearchShipmentForm(request.GET)
                context_dic['form'] = form
                if form.is_valid():
                    cleaned_form = form.cleaned_data
                    criteria = dict()
                    filter_template_dict = dict()
                    for k, v in cleaned_form.items():
                        if v or v is False:
                            criteria[k] = v
                            filter_template_dict[form.filter_keys_dict[k]] = v
                    context_dic['filter_msg'] = filter_template_dict if filter_template_dict else {'data': 'all'}
                    if criteria:
                        shipments = Shipment.objects.filter(**criteria)
                    else:
                        shipments = Shipment.objects.all()

                    if request.GET.get('action') == 'download-as-csv':
                        if shipments:
                            headers = [item.verbose_name for item in Shipment._meta.fields]
                            writer = csv.writer(Echo())
                            response = StreamingHttpResponse(((writer.writerow(headers) + writer.writerow([
                                getattr(each, items.name) for items in Shipment._meta.fields
                            ])) if counter == 0 else writer.writerow([
                                getattr(each, items.name) for items in Shipment._meta.fields
                            ]) for counter, each in enumerate(shipments)), content_type='text/csv')
                            response['Content-Disposition'] = 'attachment; filename="table.csv"'
                            return response
                        else:
                            messages.warning(request, 'No data can be downloaded as csv')

                    context_dic['total_shipments'] = shipments.count()
                    table = ShipmentTable(shipments)
                    context_dic['table'] = table
                    RequestConfig(request, paginate={'per_page': 25}).configure(table)
                    if request.GET.get('action') == 'search':
                        messages.success(request, 'found {} shipments'.format(shipments.count()))
                else:
                    messages.error(request, 'form is invalid.')

            return render(request, 'data_warehouse/shipment_search.html', context_dic)
        else:
            context_dic['filter_msg'] = {'data': 'all'}
            shipments = Shipment.objects.all()
            context_dic['total_shipments'] = shipments.count()
            table = ShipmentTable(shipments)
            context_dic['table'] = table
            RequestConfig(request, paginate={'per_page': 50}).configure(table)
            return render(request, 'data_warehouse/shipment_search.html', context_dic)
    else:
        return render(request, 'data_warehouse/shipment_search.html', context_dic)

#
# def shipment_add(request):
#     context_dic = {
#         'form': AddUnitPriceForm()
#     }
#     if request.method == 'POST':
#         form = AddUnitPriceForm(request.POST)
#         if form.is_valid():
#             new_unit_price = form.save(commit=False)
#             new_unit_price.save()
#             messages.success(request, 'Unit prices have been saved.')
#             return redirect('peripharma_billing:unit_price_index')
#         else:
#             context_dic['form'] = form
#             messages.error(request, 'form is invalid')
#     return render(request, 'peripharma_billing/unit_price/add.html', context_dic)
#
#


# def shipment_update(request, pk):
#     try:
#         selected_shipment = Shipment.objects.get(id=pk)
#     except Shipment.DoesNotExist:
#         selected_shipment = None
#     initial = {
#         'amount': Shipment.amount,
#         'billing_group': Shipment.billing_group,
#         'start_date': Shipment.start_date,
#         'end_date': Shipment.end_date
#     }
#     context_dic = {
#         'form': UpdateUnitPriceForm(initial=initial),
#         'unit_price': unit_price
#     }
#     if unit_price:
#         if request.method == 'POST':
#             form = UpdateUnitPriceForm(request.POST, initial=initial, pk=pk)
#             context_dic['form'] = form
#             if form.is_valid():
#                 if form.has_changed():
#                     cleaned_form = form.cleaned_data
#                     for each in form.changed_data:
#                         setattr(unit_price, each, cleaned_form[each])
#                     try:
#                         unit_price.save()
#                         context_dic['form'] = UpdateUnitPriceForm(request.POST, pk=pk)
#                         messages.success(request, 'unit price has been updated')
#                     except ValidationError as e:
#                         messages.error(request, e.messages)
#                 else:
#                     messages.info(request, 'nothing has been changed')
#             else:
#                 messages.error(request, 'form is invalid')
#         return render(request, 'peripharma_billing/unit_price/update.html', context_dic)
#     else:
#         return HttpResponse('unit price does not exist')