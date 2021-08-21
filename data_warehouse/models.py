from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from .misc import Zone_Choice, Surcharge_Choice, ServiceType, Delivery_Status


class Payer(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    dob = models.DateField()
    street = models.CharField(max_length=32)
    city = models.CharField(max_length=32)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=5)
    phone = models.CharField(max_length=12)
    email = models.EmailField(max_length=128)

    class Meta:
        unique_together = [['first_name', 'last_name', 'dob']]

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Shipment(models.Model):
    id = models.AutoField(primary_key=True)
    TrackingNum = models.CharField(max_length=32, unique=True)
    ShipDate = models.DateField()
    delivery_date = models.DateField(blank=True, null=True)
    service_type = models.CharField(max_length=2, choices=ServiceType)
    status = models.CharField(max_length=2, choices=Delivery_Status)
    PackageWeight = models.DecimalField(max_digits=15, decimal_places=2)
    payer = models.ForeignKey(Payer, on_delete=models.CASCADE, null=True)
    ShipperStreet = models.CharField(max_length=32)
    ShipperCity = models.CharField(max_length=32)
    ShipperState = models.CharField(max_length=2)
    ShipperZip = models.CharField(max_length=5)
    RecipientStreet = models.CharField(max_length=32)
    RecipientCity = models.CharField(max_length=32)
    RecipientState = models.CharField(max_length=2)
    RecipientZip = models.CharField(max_length=5)
    is_imported = models.BooleanField(default=False)


class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    invoice_date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payer = models.OneToOneField(Payer, on_delete=models.CASCADE, null=True)
    trans = models.IntegerField(validators=[MaxValueValidator(limit_value=9999), MinValueValidator(limit_value=0)])
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    is_emailed = models.BooleanField(default=False)


class InvoicePackage(models.Model):
    id = models.AutoField(primary_key=True)
    shipment = models.OneToOneField(Shipment, on_delete=models.CASCADE, null=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_invoiced = models.BooleanField(default=False)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class InvoiceSurcharge(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=2, choices=Surcharge_Choice)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    package = models.ForeignKey(InvoicePackage, on_delete=models.CASCADE, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    @property
    def desc(self):
        return SurchargeUnitPrice.objects.filter(code=self.code).first().desc


class SurchargeUnitPrice(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=2, choices=Surcharge_Choice)
    desc = models.CharField(max_length=64)
    from_date = models.DateField()
    to_date = models.DateField()


class ZoneUnitPrice(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=2, choices=Zone_Choice)
    desc = models.CharField(max_length=64)
    from_date = models.DateField()
    to_date = models.DateField()


class ServiceTypeUnitPrice(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=2, choices=ServiceType)
    desc = models.CharField(max_length=64)
    from_date = models.DateField()
    to_date = models.DateField()