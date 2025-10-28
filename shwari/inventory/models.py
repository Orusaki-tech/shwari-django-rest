from django.db import models
from django.utils.translation import gettext_lazy as _ # Import the translation function
from django.contrib.auth.models import AbstractUser
from django.conf import settings 
import uuid


# Create your models here.

class User(AbstractUser):
    """Custom User model extending AbstractUser to differentiate between Admin and Customer roles."""
    @property
    def is_admin(self):
        if hasattr(self, 'admin'):
            return True
        return False

    @property
    def is_customer(self):
        if hasattr(self, 'customer'):
            return True
        return False

class Admin(models.Model):
    """Model representing an Admin user with elevated privileges."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    admin_code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.user.username
    
class Customer(models.Model):
    """Model representing a Customer user."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username


#creating the color model.
class Color(models.Model):
    """Model representing a color option for products."""
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7, unique=True)
    
    def __str__(self):
        return self.name

#creating the product model.

class Product(models.Model):
    """Model representing a product in the inventory."""
    class ProductType(models.TextChoices):
        PHONE = 'PH', _('Phone')
        LAPTOP = 'LT', _('Laptop')
        ACCESSORY = 'AC', _('Accessory')

    product_type= models.CharField(max_length=2, choices= ProductType.choices, default=ProductType.ACCESSORY)
    product_name = models.CharField(max_length=255, verbose_name="Product Name", db_index=True )
    product_description = models.TextField(blank=True)
    product_image = models.ImageField(upload_to='product_images/', verbose_name='Product Image', null=True, blank=True)
    product_price = models.DecimalField(max_digits=10, decimal_places= 2)
    product_color= models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
    product_quantity = models.PositiveIntegerField(default=0, verbose_name="Internal Stock Quantity",)
    sku = models.CharField(max_length=50, unique=True, verbose_name="Stock Keeping Unit")
    related_accessories = models.ManyToManyField('self',through='ProductAccessory',symmetrical=False,related_name='parent_products',blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='products_created', null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='products_updated', null=True, blank=True)

    @property
    def in_stock(self):
        return self.product_quantity > 0
    
    def __str__(self):
        return self.product_name

class ProductAccessory(models.Model):
    """
    Links a Phone/Laptop (main_product) to an Accessory (accessory).
    """
    main_product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='product_accessories',limit_choices_to={'product_type__in': ['PH', 'LT']},verbose_name="Main Product")
    accessory = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='used_by_products',limit_choices_to={'product_type': 'AC'},verbose_name="Accessory Item")
    required_quantity = models.PositiveIntegerField(default=1,help_text="Quantity of this accessory included or required for the main product.")
    class Meta:
        unique_together = ('main_product', 'accessory')
    def __str__(self):
        return f"{self.accessory.name} for {self.main_product.name}"
    

class Review(models.Model):
    """
    Stores user feedback and rating for a specific Product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Reviewed Product")
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], help_text="Rating given to the product (1 to 5 stars).")
    comment = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-date_posted']
    def __str__(self):
        return f"Review for {self.product.name} - {self.rating} stars"


class Order(models.Model):
    """
    Represents a customer's order containing multiple products.
    """
    class order_status(models.TextChoices):
        PENDING = 'Pending', _('Pending')
        SHIPPED = 'Shipped', _('Shipped')
        DELIVERED = 'Delivered', _('Delivered')
        CANCELED = 'Canceled', _('Canceled')
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', verbose_name="Ordering User")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', verbose_name="Ordering Customer")
    products = models.ManyToManyField(Product, through='OrderItem', related_name='orders', verbose_name="Ordered Products")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=order_status.choices, default=order_status.PENDING, help_text="Current status of the order.")
    def __str__(self):
        return f"Order #{self.id} by {self.customer.user.username} - {self.status}"
    


class OrderItem(models.Model):
    """
    Intermediate model to link Orders and Products with quantity details.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name="Related Order")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items', verbose_name="Ordered Product")
    quantity = models.PositiveIntegerField(default=1, help_text="Quantity of the product ordered.")

    @property
    def sub_total(self):
        return self.product.product_price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"