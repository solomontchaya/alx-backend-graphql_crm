from django.db import models
from django.core.validators import RegexValidator, MinValueValidator

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(
            regex=r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$',
            message="Phone number must be in format +1234567890 or 123-456-7890"
        )]
    )

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} (${self.price})"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_date = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        total = sum(product.price for product in self.products.all())
        self.total_amount = total
        self.save()
        return total

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"
