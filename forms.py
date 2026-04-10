from django import forms
from .models import *

class ShopForm(forms.ModelForm):
    class Meta:
        model=Shop
        fields=['shopname','address','district','city','contactno']
class LoginForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput()) 
    class Meta:
        model=Login
        fields=['email','password']  
class UserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['name','contactno','address'] 
class LoginCheck(forms.Form):
    email=forms.CharField(max_length=100) 
    password=forms.CharField(max_length=100)
class LoginForm1(forms.ModelForm):
    class Meta:
        model=Login
        fields=['email']
class ProductForm(forms.ModelForm):
    supplierid = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        empty_label="Select a supplier",
        label="Supplier"
    )
    
    class Meta:
        model = Product
        fields = ['category', 'name', 'image', 'quantity', 'description', 'amount', 'supplierid']
class PaymentForm(forms.ModelForm):
    class Meta:
        model=PaymentDetails 
        fields=['cardname','cardno','cvv','expirymonth','expiryyear']   
class SupplierForm(forms.ModelForm):
    gender_choices=(
        ('Male','Male'),
        ('Female','Female'),
        ('other','other')  
    )
    gender=forms.ChoiceField(choices=gender_choices,widget=forms.RadioSelect())
    class Meta:
        model=Supplier
        fields=['name','gender','contactno'] 
class ReOrderForm(forms.ModelForm):
    class Meta:
        model=ReOrder
        fields=['quantity']   
class AddtoCartForm(forms.ModelForm):
    class Meta:
        model=Addtocart
        fields=['quantity']   
class DeliveryForm(forms.ModelForm):
    gender_choices=(
        ('Male','Male'),
        ('Female','Female'),
        ('other','other')  
    )
    gender=forms.ChoiceField(choices=gender_choices,widget=forms.RadioSelect())
    class Meta:
        model=Delivery
        fields=['name','gender','contactno']                         
        


    
