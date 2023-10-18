from django.db import models
import uuid


class Owner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    forename = models.CharField(max_length=128)
    surname = models.CharField(max_length=128)
    phone = models.CharField(max_length=16)
    address = models.CharField(max_length=128)
    city = models.CharField(max_length=128)

    class Meta:
        db_table = 'Owner'
    
    def __str__(self):
        return f"{self.forename} {self.surname}"

class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    balance = models.DecimalField(max_digits=19, decimal_places=2)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Account'

    def __str__(self):
        return f"Account {self.owner}"

class Deposit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=19, decimal_places=2)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Deposit'

    def __str__(self):
        return f"Deposit {self.creation_date}"

class Vehicle(models.Model):
    CLASSES = (
        (1, 'Class 1'),
        (2, 'Class 2'),
        (3, 'Class 3'),
        (4, 'Class 4')
    )
    number_plate = models.CharField(max_length=32, primary_key=True)
    type_id = models.IntegerField(choices=CLASSES)
    make = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    year = models.IntegerField()
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Vehicle'

    def __str__(self):
        return f"Vehicle {self.number_plate}"

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Transaction'

    def __str__(self):
        return f"Transaction {self.id}"
