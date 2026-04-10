import random
from django.db import models
from io import BytesIO
from django.core.files import File
import qrcode
from PIL import Image



# Create your models here.
class Shop(models.Model):
    shopname=models.CharField(max_length=100)
    address=models.CharField(max_length=100)
    district=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    contactno=models.CharField(max_length=10)   
    loginid=models.ForeignKey('Login',on_delete=models.CASCADE)
class Login(models.Model):
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=100)
    usertype=models.CharField(max_length=50)
    status=models.IntegerField(default=0) 
class User(models.Model):
    name=models.CharField(max_length=100)
    contactno=models.CharField(max_length=10)
    loginid=models.ForeignKey('Login',on_delete=models.CASCADE) 
    address=models.CharField(max_length=100)
class Product(models.Model):
    category=models.CharField(max_length=100)
    name=models.CharField(max_length=100)
    image=models.ImageField(upload_to='photo')  
    quantity=models.IntegerField()
    description=models.CharField(max_length=100)
    amount=models.IntegerField()
    loginid=models.ForeignKey('Login',on_delete=models.CASCADE)
    supplierid=models.ForeignKey('Supplier',on_delete=models.CASCADE,null=True,blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    def save(self, *args, **kwargs):
        # Save the instance to get an ID if it's new
        super().save(*args, **kwargs)

        if not self.qr_code:
            qr_data = f'Product: {self.name}\nCategory: {self.category}\nAmount: {self.amount}\nQuantity: {self.quantity}'
            qr_img = qrcode.make(qr_data)

            # Save image to memory
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)

            # Save image to the model
            filename = f'{self.name}_qr.png'
            self.qr_code.save(filename, File(buffer), save=False)

            # Save again to update the model with the QR code image
            super().save(*args, **kwargs)
class Addtocart(models.Model):
    productid=models.ForeignKey('Product',on_delete=models.CASCADE)
    loginid=models.ForeignKey('User',on_delete=models.CASCADE)
    currentdate=models.DateTimeField(auto_now_add=True) 
    status=models.IntegerField(default=0)
    cancelstatus=models.IntegerField(default=0)
    refundstatus=models.IntegerField(default=0)
    quantity=models.IntegerField()
    deliveredstatus=models.IntegerField(default=0)
    invoice=models.FileField(upload_to='invoices/')
    buystatus=models.IntegerField(default=0)
    total_amt = models.IntegerField(default=0,null=True,blank=True)
    cartid = models.CharField(max_length=5, editable=False)

    def __str__(self):
        return f"{self.cartid} - {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.cartid:
            existing_cart = Addtocart.objects.filter(loginid=self.loginid, status=0).first()
            if existing_cart:
                self.cartid = existing_cart.cartid
            else:
                self.cartid = self.generate_unique_cartid()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_cartid():
        while True:
            new_id = str(random.randint(10000, 99999))
            if not Addtocart.objects.filter(cartid=new_id, status=0).exists():
                return new_id

class PaymentDetails(models.Model):
    cardname=models.CharField(max_length=100)
    cardno=models.IntegerField()
    cvv=models.IntegerField()
    expirymonth=models.IntegerField()
    expiryyear=models.IntegerField()
    cart=models.CharField(max_length=100)
    amount=models.IntegerField()
    currentdate=models.DateTimeField(auto_now_add=True)
    loginid=models.ForeignKey('User',on_delete=models.CASCADE)
class Supplier(models.Model):
    name=models.CharField(max_length=100)
    gender=models.CharField(max_length=100)
    contactno=models.IntegerField() 
    loginid=models.ForeignKey('Login',on_delete=models.CASCADE)  
    def __str__(self):
        return self.name
class ReOrder(models.Model):
    quantity=models.IntegerField(null=True,blank=True)
    amount=models.IntegerField(null=True,blank=True)
    productid=models.ForeignKey('Product',on_delete=models.CASCADE,null=True,blank=True)
    shopid=models.ForeignKey('Shop',on_delete=models.CASCADE)
    currentdate=models.DateTimeField(auto_now_add=True) 
    cancelstatus=models.IntegerField(default=0)  
    deliveredstatus=models.IntegerField(default=0)
    buystatus=models.IntegerField(default=0)
class Delivery(models.Model):
    name=models.CharField(max_length=100)
    gender=models.CharField(max_length=100)
    contactno=models.IntegerField() 
    loginid=models.ForeignKey('Login',on_delete=models.CASCADE)  
    deliverstatus=models.IntegerField(default=0)
class Allotdelivery(models.Model) :
    deliverid=models.ForeignKey('Delivery',on_delete=models.CASCADE)
    orderid=models.ForeignKey('Addtocart',on_delete=models.CASCADE)  
    currentdate=models.DateTimeField(auto_now_add=True) 
class Allotsupplierdelivery(models.Model) :
    deliverid=models.ForeignKey('Delivery',on_delete=models.CASCADE)
    orderid=models.ForeignKey('ReOrder',on_delete=models.CASCADE)  
    currentdate=models.DateTimeField(auto_now_add=True)     

        



