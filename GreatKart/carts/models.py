from django.db import models
from store.models import Product
# Create your models here.
# create a class Cart 
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    # overide
    def __str__(self):
        return self.cart_id
    
# create class CartItem
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    cart    = models.ForeignKey(Cart, on_delete= models.CASCADE)
    quality = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def __str__ (self):
        return self.product