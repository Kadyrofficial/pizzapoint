import random
from django.db import transaction
import string
from django.db.models import Sum
from django.contrib.auth.models import (AbstractUser,
                                        User)
from django.db import models
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import m2m_changed
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from threading import local


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    password = models.CharField(max_length=255, blank=True)

    def generate_random_password(self, length=12):

        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for _ in range(length))
        return password

    def save(self, *args, **kwargs):
        if not self.password:
            self.password = self.generate_random_password()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class Banner(models.Model):
    name_en = models.CharField(max_length=100)
    name_hu = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/banners/')
    queue = models.IntegerField(null=True)

    def __str__(self):
        return self.name_en


class Category(models.Model):
    name_en = models.CharField(max_length=100)
    name_hu = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/categories', blank=True)
    queue = models.IntegerField()

    def __str__(self):
        return self.name_en


class Product(models.Model):
    name_en = models.CharField(max_length=100)
    name_hu = models.CharField(max_length=100)
    description_en = models.TextField()
    description_hu = models.TextField()
    price = models.DecimalField(max_digits=15, decimal_places=2)
    discount = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    new_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_best = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='images/products/thumbnails')
    image = models.ImageField(upload_to='images/products/images')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def save(self, *args, **kwargs):
        result = self.price * (100 - self.discount) / 100
        self.new_price = Decimal(result).quantize(Decimal('0.1'))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_en




class OrderItem(models.Model):

    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        ACTIVE = 'Active', 'Active'
        COMPLETED = 'Completed', 'Completed'
        CANCELED = 'Canceled', 'Canceled'

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='product')
    created_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    quantity = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)
    status = models.CharField(max_length=50, choices=Status, default=Status.PENDING, editable=False)

    def save(self, *args, **kwargs):
        result = self.quantity * self.product.new_price
        self.total = Decimal(result).quantize(Decimal('0.1'))
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.user.username


class OrderItemRelation(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    order_item = models.ForeignKey('OrderItem', on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        print(f"Deleting OrderItemRelation ID: {self.id}")
        if self.order_item:
            print(f"Deleting associated OrderItem ID: {self.order_item.id}")
        super().delete(*args, **kwargs)


class Order(models.Model):

    class Status(models.TextChoices):
        ACTIVE = 'Active', 'Active'
        COMPLETED = 'Completed', 'Completed'
        CANCELED = 'Canceled', 'Canceled'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', editable=False)
    created_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    sum_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    order_items = models.ManyToManyField(OrderItem, related_name='order_items', through='OrderItemRelation', blank=True, editable=False)
    status = models.CharField(max_length=50, choices=Status, default=Status.ACTIVE)



    def save(self, *args, **kwargs):

        self.full_clean()

        if not self.pk:
            pending_items = OrderItem.objects.filter(status=OrderItem.Status.PENDING)
            if not pending_items.exists():
                raise ValidationError("No pending OrderItems available to assign a user.")
            super().save(*args, **kwargs)
            self.order_items.set(pending_items)
            self.order_items.update(status=self.status)
        else:
            current_status = Order.objects.get(pk=self.pk).status
            if current_status in [Order.Status.COMPLETED, Order.Status.CANCELED]:
                raise ValidationError(
                    _("You cannot modify completed or canceled orders.")
                )
            super().save(*args, **kwargs)
            self.order_items.update(status=self.status)

    


    def __str__(self):
        return self.user.username
    

def update_order_total(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        total_sum = sum(item.total for item in instance.order_items.all())
        instance.sum_total = Decimal(total_sum).quantize(Decimal('0.01'))
        instance.save(update_fields=['sum_total'])


m2m_changed.connect(update_order_total, sender=Order.order_items.through)

local_storage = local()
local_storage.deletion_in_progress = False

@receiver(pre_delete, sender=OrderItemRelation)
def delete_related_order_item(sender, instance, **kwargs):
    # Avoid recursive calls by checking the thread-local flag
    if not getattr(local_storage, "deletion_in_progress", False):
        try:
            local_storage.deletion_in_progress = True
            if instance.order_item:
                print(f"Deleting associated OrderItem ID: {instance.order_item.id}")
                instance.order_item.delete()
        finally:
            local_storage.deletion_in_progress = False
