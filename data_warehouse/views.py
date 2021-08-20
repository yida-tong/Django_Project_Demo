import io
import csv
import requests
import datetime
import decimal
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.contrib import messages
from .models import *


def index(request):
    context_dict = {'payers_num': Payer.objects.count()
                    }
    return render(request, 'data_warehouse/dashboard.html', context_dict)


def csv_downloader(request):
    if request.method == 'GET' and len(request.GET) > 0:
        if request.GET['action'] == 'payers':
            url = 'https://www.dropbox.com/s/eo5s6owm5saqa25/payer%20%281%29.csv?raw=1'
            file_name = 'payers.csv'
        elif request.GET['action'] == 'shipments':
            url = 'https://www.dropbox.com/s/7q4x19ueer3ubyd/payer.csv?raw=1'
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
    if request.method == 'POST' and request.POST['action'] == 'upload':
        payer_file = request.FILES['payers_csv']
        # shipment_file = request.FILES['shipment_csv']
        if not payer_file.name.endswith('.csv'):
            messages.error(request, 'Not a csv file')
            return render(request, 'data_warehouse/dashboard.html', {})
        if payer_file.multiple_chunks():
            messages.error(request, 'File size too big (%.2f MB)' % (payer_file.size / (1000 * 1000)))
            return render(request, 'data_warehouse/dashboard.html', {})

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
            messages.success(request, 'Data is added')
        else:
            messages.warning(request, 'No data is read')
        return render(request, 'data_warehouse/dashboard.html')
    else:
        return HttpResponseBadRequest()


def reset(request):
    if request.method == 'POST' and request.POST['action'] == 'reset':
        Payer.objects.all().delete()
        messages.success(request, 'Reset done')
        return render(request, 'data_warehouse/dashboard.html')
    else:
        return HttpResponseBadRequest()




#
# def shipment_listing(request):
#     return
#
#
# def import_shipment(request):
#     # calculate base rate based on delivery distance, weight, and service type
#
#
#     return
#
#
# def apply_surcharge(request):
#     return



# def unit_price_management(request):
#     return
#
#
