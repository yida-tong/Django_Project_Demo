from django.urls import path
from . import views

app_name = 'data_warehouse'

urlpatterns = [
    path('index/', views.index, name='index'),
    path('csv_downloader/', views.csv_downloader, name='csv_downloader'),
    path('csv_uploader/', views.csv_uploader, name='csv_uploader'),
    path('reset/', views.reset, name='reset'),
    path('shipment_import/', views.shipment_import, name='shipment_import'),
    path('video_player/', views.video_player, name='video_player'),
    path('shipment_search/', views.shipment_search, name='shipment_search'),
    # path('shipment_add/', views.shipment_add, name='shipment_add'),
    # path('shipment_update/', views.shipment_update, name='shipment_edit'),
    # path('shipment_delete/', views.shipment_delete, name='shipment_delete'),
]