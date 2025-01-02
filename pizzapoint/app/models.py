import random
import string
from django.db.models import Sum
from django.contrib.auth.models import (AbstractUser,
                                        User)
from django.db import models
from decimal import Decimal
from django.utils.translation import gettext_lazy as _

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
    discount = models.DecimalField(max_digits=5, decimal_places=0)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    created_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    quantity = models.DecimalField(max_digits=5, decimal_places=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        result = self.quantity * self.product.new_price
        self.total = Decimal(result).quantize(Decimal('0.1'))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    sum_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    orders = models.ManyToManyField(OrderItem, related_name='orders', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate the sum of the total prices of all related OrderItem instances
        total_sum = sum(item.total for item in self.orders.all())
        self.sum_total = Decimal(total_sum).quantize(Decimal('0.1'))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username
