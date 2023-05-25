from django.db import models
from store.models import Product,Variation
from accounts.models import Account
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
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    variations = models.ManyToManyField(Variation,blank=True)
    cart    = models.ForeignKey(Cart, on_delete= models.CASCADE,null=True)
    quality = models.IntegerField()
    is_active = models.BooleanField(default=True)
    
    def sub_total(self):
        return self.product.price * self.quality
    
    def __unicode__ (self):
        return self.product