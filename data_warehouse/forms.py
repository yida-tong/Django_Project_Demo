from django import forms


class SearchShipmentForm(forms.Form):
    id = forms.IntegerField(
        label='id',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        required=False
    )
    TrackingNum = forms.CharField(
        label='Tracking Number',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )
    ShipDate__gte = forms.DateField(
        label='From ShipDate',
        widget=forms.DateInput(attrs={'class': 'form-control datepicker'}, format='%Y-%m-%d'),
        required=False
    )
    ShipDate__lte = forms.DateField(
        label='To ShipDate',
        widget=forms.DateInput(attrs={'class': 'form-control datepicker'}, format='%Y-%m-%d'),
        required=False
    )

    filter_keys_dict = {
        'id': 'id',
        'TrackingNum': 'Tracking Number',
        'ShipDate__gte': 'from date',
        'ShipDate__lte': 'to date'
    }

    def clean(self):
        cleaned_data = super(SearchShipmentForm, self).clean()

        from_date = cleaned_data.get('ShipDate__gte')
        to_date = cleaned_data.get('ShipDate__lte')
        if from_date and to_date:
            if from_date > to_date:
                self.add_error('ShipDate__gte', 'from date is greater than to date')
                self.add_error('ShipDate__lte', 'to date is less than from date')
#
#
# class AddShipmentForm(forms.ModelForm):
#     amount = forms.DecimalField(
#         widget=forms.TextInput(attrs={'class': 'form-control'}),
#         max_digits=15,
#         decimal_places=2,
#     )
#     billing_group = forms.ModelChoiceField(
#         widget=forms.Select(attrs={'class': 'form-control'}),
#         queryset=Billing_Group.objects.all(),
#         empty_label=None,
#         required=True,
#         label='billing group',
#     )
#     start_date = forms.DateField(
#         widget=forms.DateInput(format='%m/%d/%Y', attrs={'class': 'datepicker form-control'}),
#         label='start date',
#         help_text='Format: mm/dd/yyyy'
#     )
#     end_date = forms.DateField(
#         widget=forms.DateInput(format='%m/%d/%Y', attrs={'class': 'datepicker form-control'}),
#         label='end date test',
#         help_text='Format: mm/dd/yyyy'
#     )
#
#     class Meta:
#         model = Shipment_Unit_Price
#         fields = ['amount', 'billing_group', 'start_date', 'end_date']
#
#     def clean(self):
#         cleaned_data = super(AddUnitPriceForm, self).clean()
#         start_date = cleaned_data.get('start_date')
#         end_date = cleaned_data.get('end_date')
#         if start_date and end_date:
#             if start_date > end_date:
#                 self.add_error('start_date', 'start date is greater than end date')
#                 self.add_error('end_date', 'end date is less than start date')
#             else:
#                 billing_group = cleaned_data.get('billing_group')
#                 new_start_date = cleaned_data.get('start_date')
#                 new_end_date = cleaned_data.get('end_date')
#                 unit_prices = Shipment_Unit_Price.objects.filter(billing_group=billing_group)
#                 if unit_prices.count():
#                     for each in unit_prices:
#                         #  start1__________end1<--delta-->start2__________end2
#                         latest_start = max(new_start_date, each.start_date)
#                         earliest_end = min(new_end_date, each.end_date)
#                         delta = (latest_start - earliest_end)
#                         if delta <= datetime.timedelta(0):
#                             raise forms.ValidationError('Error. Price has overlap.')
#         else:
#             raise forms.ValidationError('Error. Please follow the rule of date format.')

#
# class EditShipmentForm(AddShipmentForm):
#     def __init__(self, *args, **kwargs):
#         try:  # pk exists
#             self.pk = kwargs.pop('pk')
#             super().__init__(*args, **kwargs)
#         except:  # pk doesn't exist. (avoid errors when run unbound form)
#             super().__init__(*args, **kwargs)
#
#     def clean(self):
#         cleaned_data = super(AddShipmentForm, self).clean()
#         edited_start_date = cleaned_data.get('start_date')
#         edited_end_date = cleaned_data.get('end_date')
#         if edited_start_date and edited_end_date:
#             if edited_start_date > edited_end_date:
#                 self.add_error('start_date', 'start date is greater than end date')
#                 self.add_error('end_date', 'end date is less than start date')
#             else:
#                 billing_group = cleaned_data.get('billing_group')
#                 unit_prices = Shipment_Unit_Price.objects.filter(billing_group=billing_group).exclude(
#                     id=self.pk)  # itself is an exception
#                 if unit_prices.count() > 1:
#                     for each in unit_prices:
#                         #  start1__________end1<--delta-->start2__________end2
#                         latest_start = max(edited_start_date, each.start_date)
#                         earliest_end = min(edited_end_date, each.end_date)
#                         delta = (latest_start - earliest_end)
#                         if delta <= datetime.timedelta(0):
#                             raise forms.ValidationError('Error. Price has overlap from.')
#
#         else:
#             raise forms.ValidationError('Error. Please follow the rule of date format.')