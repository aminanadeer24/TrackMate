import json
from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from .forms import *
from django.db.models import Q
from django.contrib import messages
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from django.conf import settings


def adminindex(request):
    f=request.session.get('admin_id')
    if not f:
        messages.error(request,'You are not a valid admin,please login and try again')
        return redirect('loginindex')
    a=User.objects.all().count()
    b=Shop.objects.all().count()
    c=Supplier.objects.all().count()
    d=Delivery.objects.all().count()
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    category = request.GET.get('category')

    sales_qs = Addtocart.objects.filter(buystatus=1)

    if from_date and to_date:
        sales_qs = sales_qs.filter(currentdate__date__range=[from_date, to_date])
    if category:
        sales_qs = sales_qs.filter(productid__category__icontains=category)

    # Daily Sales
    daily_sales = sales_qs.extra({'date': "DATE(currentdate)"}).values('date') \
        .annotate(total_sales=Sum('total_amt')) \
        .order_by('date')

    # Monthly Revenue
    monthly_revenue = sales_qs.annotate(month=F('currentdate__month')) \
        .values('month', 'productid__name') \
        .annotate(revenue=Sum('total_amt')) \
        .order_by('month')

    # Top Products
    top_products = sales_qs.values('productid__name') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold')[:5]

    # Inventory Turnover
    total_sales_qty = sales_qs.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_inventory = Addtocart.objects.aggregate(Sum('quantity'))['quantity__sum'] or 1
    turnover_rate = round(total_sales_qty / total_inventory, 2)
    total_revenue = sales_qs.aggregate(Sum('total_amt'))['total_amt__sum'] or 0


    return render(request,'adminindex.html',{'a':a,'b':b,'c':c,'d':d, 'daily_sales': json.dumps(list(daily_sales), cls=DjangoJSONEncoder),
        'monthly_revenue': json.dumps(list(monthly_revenue),    cls=DjangoJSONEncoder),
        'top_products': top_products,
        'turnover_rate': turnover_rate,
        'from': from_date,
        'to': to_date,
        'category': category,
        'total_revenue' : total_revenue})
def userindex(request):
    return render(request,'userindex.html')  
def loginindex(request):
    if request.method=='POST':
        form=LoginCheck(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            if email=="admin@gmail.com" and password=="Admin@123":
                request.session['admin_id']="admin" 
                return redirect('adminindex')   

            try:
                a=Login.objects.get(email=email)
                
                if a.password==password and a.usertype=='SHOP' and a.status == 1 :
                    request.session['shop_id']=a.id
                    request.session['email']=a.email
                    return redirect('shophomepage')
                elif a.password==password and a.usertype=='USER':
                    request.session['user_id']=a.id
                    request.session['email']=a.email
                    return redirect('userhomepage') 
                elif a.password==password and a.usertype=='SUPPLIER' and a.status == 1:
                    request.session['supplier_id']=a.id
                    request.session['email']=a.email
                    return redirect('supplierhomepagenew')   
                elif a.password==password and a.usertype=='DELIVERY' and a.status == 1:
                    request.session['delivery_id']=a.id
                    request.session['email']=a.email
                    return redirect('deliveryhome')   

                else:
                    messages.error(request,'Invalid password') 
            except Login.DoesNotExist:
                messages.error(request,'user does not exist')              
    else:
        form=LoginCheck()
    return render(request,'loginindex.html',{'form':form}) 
def shopregistration(request):
    if request.method=='POST':
        form1=ShopForm(request.POST)
        form2=LoginForm(request.POST)

        if form1.is_valid() and form2.is_valid():
            a=form2.save(commit=False)
            a.usertype="SHOP"
            a.save()
            b=form1.save(commit=False)
            b.loginid=a
            b.save()
            return redirect('shopregistration')
    else:
       form1=ShopForm()
       form2=LoginForm()
    return render(request,'shopregistration.html',{'form':form1,'forms':form2})         
def userregistration(request):
    if request.method=='POST':
        form1=UserForm(request.POST)
        form2=LoginForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            a=form2.save(commit=False)
            a.usertype="USER"
            a.save()
            b=form1.save(commit=False)
            b.loginid=a
            b.save()
            return redirect('userregistration')
    else:
        form1=UserForm()
        form2=LoginForm() 
    return render(request,'userregistration.html',{'form':form1,'forms':form2})           
def adminshop(request):
    a=request.session.get('admin_id')
    if not a:
        messages.error(request,'You are not a valid admin,please login and try again')
        return redirect('loginindex')
    shop=Shop.objects.all()
    return render(request,'adminshopview.html',{'user':shop}) 
def adminuser(request):
    a=request.session.get('admin_id')
    if not a:
        messages.error(request,'You are not a valid admin,please login and try again')
        return redirect('loginindex')
    user=User.objects.all()
    return render(request,'adminuserview.html',{'user1':user}) 
def shophomepage(request):
    shop=request.session.get('shop_id')
    
    if not shop:
        messages.error(request,'You are not a valid admin,please login and try again')
        return redirect('loginindex')
    s=get_object_or_404(Shop,loginid=shop)
    products = Product.objects.filter(loginid=shop)
    low_stock_products = products.filter(quantity__lt=10)

    return render(request, 'shophomepage.html', {
        'products': products,
        'low_stock_products': low_stock_products
    })
def userhomepage(request):
    a=request.session.get('user_id')
    if not a:
        messages.error(request,'You are not a valid admin,please login and try again')
        return redirect('loginindex')
    return render(request,'userhomepage.html')  
# def shop_delete(request,id):
#     shop=get_object_or_404(id=id) 
#     shop.delete()
#     return redirect('shophomepage')   
# def user_delete(request,id):
#     user=get_object_or_404(id=id)
#     user.delete()
#     return redirect('userhomepage')   
def userprofile(request):
    user=request.session.get('user_id') 
    if not user:
        messages.error(request,'You are not a valid user,please login and try again')
        return redirect('loginindex')
    u=get_object_or_404(Login,id=user) 
    user_data=get_object_or_404(User,loginid=u.id)  
    logindata=get_object_or_404(Login,id=u.id) 
    if request.method=='POST':
        form1=UserForm(request.POST,instance=user_data)
        # form2=LoginForm1(request.POST,instance=logindata)
        if form1.is_valid():
            # a=form2.save(commit=False)
            # a.usertype="USER"
            # a.save()
            # b=form1.save(commit=False)
           
            form1.save()
            return redirect('userhomepage')
    else:
        form1=UserForm(instance=user_data)
        # form2=LoginForm1(instance=logindata)
    return render(request,'userprofileedit.html',{'form':form1})   
def shopprofile(request):
    shop=request.session.get('shop_id') 
    if not shop:
        messages.error(request,'You are not valid shop,please login and try again')
        return redirect('loginindex')  
    s=get_object_or_404(Login,id=shop) 
    shopdata=get_object_or_404(Shop,loginid=s.id)  
    logindata=get_object_or_404(Login,id=s.id)
    if request.method=='POST':
        form1=ShopForm(request.POST,instance=shopdata)
        # form2=LoginForm1(request.POST,instance=logindata)
        if form1.is_valid():
            # form2.save() 
            form1.save()
            return redirect('shophomepage')
    else:
        form1=ShopForm(instance=shopdata)
        # form2=LoginForm1(instance=logindata)
    return render(request,'shopprofileedit.html',{'form':form1})  
def productdetail(request):
    shop=request.session.get('shop_id')  
    if not shop:
        messages.error(request,'You are not valid shop,please login and try again') 
        return redirect('loginindex')
    s=get_object_or_404(Login,id=shop) 
    if request.method=='POST':
        form1=ProductForm(request.POST,request.FILES)

        if form1.is_valid():
            a=form1.save(commit=False) 
            a.loginid=s
            a.save()
            return redirect('shophomepage')   
    else:
        form1=ProductForm() 
    return render(request,'product.html',{'form':form1})
def viewproduct(request):
    shop=request.session.get('shop_id')
    a=get_object_or_404(Login,id=shop)
    if not shop:
        messages.error(request,'You are not valid shop,please login and try again')
        return redirect('loginindex')
    product=Product.objects.filter(loginid=a).order_by('category')
    return render(request,'viewproduct.html',{'product':product})    
def editproduct(request,id):
    shop=request.session.get('shop_id')
    if not shop:
        messages.error(request,'You are not valid shop,please login and try again')
        return redirect('loginindex')
    product=get_object_or_404(Product,id=id) 
    if request.method=='POST':
         form=ProductForm(request.POST,request.FILES,instance=product)  
         if form.is_valid():
            form.save()
            return redirect('viewproduct')
    else:
        form=ProductForm(instance=product)
    return render(request,'editproduct.html',{'form':form}) 
def deleteproduct(request,id):
    shop=request.session.get('shop_id')
    if not shop:
        messages.error(request,'You are not valid shop,please login and try again')
        return redirect('loginindex')
    product=get_object_or_404(Product,id=id)
    product.delete()
    return redirect('viewproduct')   
def listproduct(request):
    user=request.session.get('user_id')
    if not user:
        messages.error(request,'You are not valid user,please login and try again')
        return redirect('loginindex')
    product = Product.objects.all().order_by('category')  # or 'category' depending on the model

    a=request.GET.get('search')
    if a:
        product=Product.objects.filter(Q(category__icontains=a)|Q(name__icontains=a))
    return render(request,'productlist.html',{'product':product})  


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, User, Addtocart  # adjust based on your app structure

def addtocart(request, id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, 'You are not a valid user, please login and try again')
        return redirect('loginindex')

    product = get_object_or_404(Product, id=id)
    total_available_quantity = product.quantity
    unit_price = product.amount
    user = get_object_or_404(User, loginid=user_id)

    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity'))
        except (TypeError, ValueError):
            messages.error(request, 'Invalid quantity entered.')
            return redirect('addtocart', id=id)

        if quantity <= 0:
            messages.error(request, 'Quantity must be greater than zero.')
        elif quantity <= total_available_quantity:
            total_amt = quantity * unit_price

            # Create the cart entry with total_amt stored
            Addtocart.objects.create(
                productid=product,
                loginid=user,
                quantity=quantity,
                total_amt=total_amt,
                buystatus=0  # assuming this is the default for new cart items
            )
            return redirect('addtocartorders')
        else:
            messages.error(
                request,
                f'Total quantity available is {total_available_quantity}. Please order less than this amount.'
            )

    return render(request, 'addtocart.html', {'product': product})

def userview(request):
    p=request.session.get('user_id')
    if not p:
        messages.error(request,'You are not valid user,please login and try again')
        return redirect('loginindex')
    logid=get_object_or_404(User,loginid=p)
    product=Product.objects.filter(loginid=logid.id)
    return render(request,'cart.html',{'product':product})
def  userdelete(request,id):
     p=request.session.get('user_id')
     if not p:
        messages.error(request,'You are not valid user,please login and try again')
        return redirect('loginindex')
     product=get_object_or_404(Product,id=id)
     product.delete()
     return redirect('userview')

def userproductview(request):
    user=request.session.get('user_id')
    if not user:
        messages.error(request,'You are not valid user,please login and try again')
        return redirect('loginindex')
   
    a=get_object_or_404(User,loginid=user)
    print(a)
    product=Addtocart.objects.filter(loginid=a.id, status=1)
    return render(request,'userproductview.html', {'product':product})

def shopproductview(request):  
    shop=request.session.get('shop_id')
    if not shop:
        messages.error(request,'You are not valid shop,please login and try again')
        return redirect('loginindex')
    a=get_object_or_404(Login,id=shop)
    products=Addtocart.objects.filter(productid__loginid=a, status=1)
    return render(request, 'shopproductpaymentview.html', {'product':products})
def cancelstatus(request,id):
    c=get_object_or_404(Addtocart,id=id)
    c.cancelstatus = 1
    c.save()
    return redirect('userproductview')
def refundpayment(request,id):
    r=get_object_or_404(Addtocart,id=id)
    r.refundstatus=1
    r.save()
    return render(request,'refundpayment.html') 
def supplierregistration(request):
    if request.method=='POST':
        form1=SupplierForm(request.POST) 
        form2=LoginForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            a=form2.save(commit=False)
            a.usertype="SUPPLIER"
            a.save()
            b=form1.save(commit=False)
            b.loginid=a
            b.save()
            return redirect('supplierregistration')
    else:
        form1=SupplierForm()
        form2=LoginForm()
    return render(request,'supplierregistration.html',{'form':form1,'forms':form2}) 
def adminsupplier(request):
    a=request.session.get('admin_id') 
    if not a:
        messages.error(request,'You are not valid admin,please login and try again')
        return redirect('loginindex')  
    supplier=Supplier.objects.all()
    return render(request,'adminsupplierview.html',{'supp':supplier}) 
def supplierhomepagenew(request):
    supplier=request.session.get('supplier_id') 
    if not supplier:
        messages.error(request,'You are not valid supplier,please login and try again')
        return redirect('loginindex')  
    return render(request,'supplierhomepagenew.html') 
def supplierprofile(request):
    supplier=request.session.get('supplier_id') 
    if not supplier:
        messages.error(request,'You are not valid supplier,please login and try again')
        return redirect('loginindex')  
    s=get_object_or_404(Login,id=supplier) 
    supplierdata=get_object_or_404(Supplier,loginid=s.id)  
    logindata=get_object_or_404(Login,id=s.id)
    if request.method=='POST':
        form1=SupplierForm(request.POST,instance=supplierdata)
        # form2=LoginForm1(request.POST,instance=logindata)
        if form1.is_valid():
            # form2.save()
            form1.save()
            return redirect('supplierhomepagenew')
    else:
        form1=SupplierForm(instance=supplierdata)
        # form2=LoginForm1(instance=logindata)
    return render(request,'supplierprofile.html',{'form1':form1})  
def listsuppliers(request):
    supplier=request.session.get('supplier_id') 
    if not supplier:
        messages.error(request,'You are not valid supplier,please login and try again')
        return redirect('loginindex') 
    supplier=Supplier.objects.all()
    a=request.GET.get('search')
    if a:
        supplier=Supplier.objects.filter(Q(name__icontains=a)|Q(gender__icontains=a))
    return render(request,'suppliers.html',{'supplier':supplier})  

def supplierview(request):
    s=request.session.get('supplier_id')
    if not s:
        messages.error(request,'You are not valid supplier,please login and try again')
        return redirect('loginindex') 
    a=get_object_or_404(Supplier,loginid=s)
    supplier=ReOrder.objects.filter(productid__supplierid=a)
    return render(request,'supplierview.html',{'user':supplier})  
def shopreorderview(request):
    s=request.session.get('shop_id')
    if not s:
        messages.error(request,'You are not valid shop,please login and try again')
        return redirect('loginindex') 
    a=get_object_or_404(Shop,loginid=s) 
    shop=ReOrder.objects.filter(shopid=a)
    return render(request,'shopreorderproduct.html',{'user':shop})
def reordercancelstatus(request,id):
    c=get_object_or_404(ReOrder,id=id)
    c.cancelstatus=1
    c.save()
    return redirect('shopreorderview') 
# def editreorder(request,id): 
#     product=get_object_or_404(ReOrder,id=id) 
#     if request.method=='POST':
#          form=ReOrderForm(request.POST,request.FILES,instance=product)  
#          if form.is_valid():
#             form.save()
#             return redirect('shopreorderview')
#     else:
#         form=ReOrderForm(instance=product)
    return render(request,'editreorder.html',{'form':form})   
def deletereorderproduct(request,id):
    product=get_object_or_404(ReOrder,id=id)
    product.delete()
    return redirect('shopreorderview')   
      
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

def salesdetails(request):
    s = request.session.get('shop_id')
    if not s:
        messages.error(request,'You are not valid supplier,please login and try again')
        return redirect('loginindex') 
    date_str = request.POST.get('date')  # format: 'YYYY-MM-DD'
    sales = []

    if date_str:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        start = make_aware(datetime.combine(date, datetime.min.time()))
        end = make_aware(datetime.combine(date, datetime.max.time()))

        b = get_object_or_404(Login, id=s)
        sales = Addtocart.objects.filter(productid__loginid=b, currentdate__range=(start, end))
        print(sales)

    return render(request, 'salesdetails.html', {'sales': sales})

def index(request):
    return render(request,'index.html')  
def logoutview(request):
    request.session.flush()
    return redirect('index')  
def shopapprove(request,id):
    a=get_object_or_404(Login,id=id)
    a.status=1
    a.save()
    return redirect('adminshop')  
def shopreject(request,id):
    b=get_object_or_404(Login,id=id)  
    b.status=2
    b.save()
    return redirect('adminshop')        
def supplierapprove(request,id):
    a=get_object_or_404(Login,id=id)
    a.status=1
    a.save()
    return redirect('adminsupplier')  
def supplierreject(request,id):
    b=get_object_or_404(Login,id=id)  
    b.status=2
    b.save()
    return redirect('adminsupplier')   
def deliveryregistration(request):
    if request.method=='POST':
        form1=DeliveryForm(request.POST) 
        form2=LoginForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            a=form2.save(commit=False)
            a.usertype="DELIVERY"
            a.save()
            b=form1.save(commit=False)
            b.loginid=a
            b.save()
            return redirect('deliveryregistration')
    else:
        form1=DeliveryForm()
        form2=LoginForm()
    return render(request,'deliveryregistration.html',{'form':form1,'forms':form2})          
def deliveryhome(request):
    delivery=request.session.get('delivery_id') 
    if not delivery:
        messages.error(request,'You are not valid deliverboy,please login and try again')
        return redirect('loginindex')   
    return render(request,'deliveryhome.html') 
def deliveryprofile(request):
    delivery=request.session.get('delivery_id') 
    if not delivery:
        messages.error(request,'You are not valid deliverboy,please login and try again')
        return redirect('loginindex')   
    s=get_object_or_404(Login,id=delivery) 
    deliverydata=get_object_or_404(Delivery,loginid=s.id)  
    logindata=get_object_or_404(Login,id=s.id)
    if request.method=='POST':
        form1=DeliveryForm(request.POST,instance=deliverydata)
        # form2=LoginForm1(request.POST,instance=logindata)
        if form1.is_valid():
            # form2.save()
            form1.save()
            return redirect('deliveryhome')
    else:
        form1=DeliveryForm(instance=deliverydata)
        # form2=LoginForm1(instance=logindata)
    return render(request,'deliveryprofile.html',{'form':form1})   
def admindeliver(request):
    a=request.session.get('admin_id')
    if not a:
        messages.error(request,'You are not a valid admin,please login and try again')
        return redirect('loginindex')
    deliver=Delivery.objects.all()
    return render(request,'admindeliverview.html',{'deliver':deliver})  
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Delivery, Addtocart  # Adjust import path based on your structure

def listdelivers(request):
    delivery_id = request.session.get('delivery_id')
    
    if not delivery_id:
        messages.error(request, 'You are not a valid delivery boy, please login and try again')
        return redirect('loginindex')

    # Get the Delivery object
    try:
        delivery_person = Delivery.objects.get(loginid=delivery_id)
    except Delivery.DoesNotExist:
        messages.error(request, 'Delivery person not found')
        return redirect('loginindex')

    # Check deliverstatus
    if delivery_person.deliverstatus != 0:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('deliveryhome')

    # Only show deliveries if the above condition passes
    deliver = Addtocart.objects.filter(buystatus=2)

    return render(request, 'deliverlist.html', {'deliver': deliver, 'id': delivery_id})

def listsupplierdeliver(request):
    delivery=request.session.get('delivery_id')
    if not delivery:
        messages.error(request,'You are not valid deliverboy,please login and try again')
        return redirect('loginindex')  
    try:
        delivery_person = Delivery.objects.get(loginid=delivery)
    except Delivery.DoesNotExist:
        messages.error(request, 'Delivery person not found')
        return redirect('loginindex')

    # Check deliverstatus
    if delivery_person.deliverstatus != 0:
        messages.error(request, 'You are not authorized to view this page')
        return redirect('deliveryhome')
 
    reorder=ReOrder.objects.filter(buystatus=2)
    print(reorder)
    return render(request,'listsupplierdeliver.html',{'reorder':reorder, 'id':delivery})  

def allotdeliver(request,id):
    deliver=request.session.get('delivery_id')
    if not deliver:
        messages.error(request,'You are not valid deliverboy,please login and try again')
        return redirect('loginindex')   
    a=get_object_or_404(Delivery,loginid=deliver)
    b=get_object_or_404(Addtocart,id=id)
    a.save()
    b.buystatus=3 #accept delivery boy
    b.save()
    if Allotdelivery.objects.filter(deliverid=a,orderid=b):
        messages.error(request,'Already Assigned')
        return redirect('deliveryhome')
    else:
        Allotdelivery.objects.create(deliverid=a,orderid=b)
        return redirect('deliveryhome')
    
def deliverallotview(request):
    a=request.session.get('delivery_id')
    if not a:
        messages.error(request,'You are not valid deliverboy,please login and try again')
        return redirect('loginindex')   
    b=get_object_or_404(Delivery,loginid=a)
    data=Allotdelivery.objects.filter(deliverid=b)
    return render(request,'deliveryview.html',{'data':data})

def deliveredstatus_product(request,id):
    a=request.session.get('delivery_id')
    b=get_object_or_404(Delivery,loginid=a)
    c=get_object_or_404(Addtocart,id=id)
    c.deliveredstatus = 1
    c.save()
    b.deliverstatus = 0
    b.save()
    return redirect('deliveryhome')
def deliverapprove(request,id):
    a=get_object_or_404(Login,id=id)
    a.status=1
    a.save()
    return redirect('admindeliver')  
def deliverreject(request,id):
    b=get_object_or_404(Login,id=id)  
    b.status=2
    b.save()
    return redirect('admindeliver')  
# from django.db import transaction

# @transaction.atomic
# def payment(request, cartid, amount):
#     user = request.session.get('user_id')
#     if not user:
#         messages.error(request, 'You are not a valid supplier, please login and try again')
#         return redirect('loginindex')

#     a = get_object_or_404(User, loginid=user)
#     cart_items = Addtocart.objects.filter(cartid=cartid, loginid=a, buystatus=0)

#     if not cart_items.exists():
#         messages.error(request, 'No items found in cart.')
#         return redirect('cart')

#     total_amount = 0
#     product_updates = {}

#     # First pass: check stock & compute totals
#     for item in cart_items:
#         product = item.productid
#         quantity = item.quantity

#         if product.quantity < quantity:
#             messages.error(request, f"Not enough stock for {product.name}.")
#             return redirect('cart')

#         total_amount += quantity * product.amount
#         product_updates[product.id] = product_updates.get(product.id, 0) + quantity

#     if request.method == 'POST':
#         form = PaymentForm(request.POST)
#         if form.is_valid():
#             invoice_path = save_invoice_to_file(a, cart_items, total_amount, cartid)

#             for item in cart_items:
#                 # Save payment
#                 p = form.save(commit=False)
#                 p.loginid = a
#                 p.cart = item.cartid
#                 p.amount = item.quantity * item.productid.amount
#                 p.save()

#                 # Update cart item
#                 item.status = 1
#                 item.buystatus = 1
#                 item.total_amt = item.quantity * item.productid.amount

#                 # Save invoice file (open fresh each time)
#                 with open(invoice_path, 'rb') as f:
#                     item.invoice.save(os.path.basename(invoice_path), File(f), save=False)

#                 item.save()  # Save after setting invoice

#             # Update product stock
#             for product_id, qty in product_updates.items():
#                 product = Product.objects.get(id=product_id)
#                 product.quantity -= qty
#                 product.save()

#             return render(request, 'payment_success.html', {
#                 'invoice_url': settings.MEDIA_URL + cart_items.first().invoice.name
#             })
#     else:
#         form = PaymentForm()

#     return render(request, 'payment.html', {'form': form})





import os
import random
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.core.files.base import File
from .models import Addtocart, PaymentDetails, Product
from django.contrib.auth.decorators import login_required
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.utils import timezone


def make_payment(request, cartid):
    user = request.user
    cart_items = Addtocart.objects.filter(cartid=cartid, loginid=user, status=0, buystatus=0)
    
    if not cart_items.exists():
        return HttpResponse("No items in cart to pay for.")

    if request.method == "POST":
        # Get form data
        cardname = request.POST.get("cardname")
        cardno = request.POST.get("cardno")
        cvv = request.POST.get("cvv")
        expirymonth = request.POST.get("expirymonth")
        expiryyear = request.POST.get("expiryyear")

        # Total amount calculation
        total_amount = sum(item.productid.amount * item.quantity for item in cart_items)

        # Save PaymentDetails
        PaymentDetails.objects.create(
            cardname=cardname,
            cardno=cardno,
            cvv=cvv,
            expirymonth=expirymonth,
            expiryyear=expiryyear,
            cart=cartid,
            amount=total_amount,
            loginid=user,
        )

        # Generate invoice
        invoice_file = generate_invoice(cart_items, total_amount, user)

        # Update cart items
        for item in cart_items:
            item.buystatus = 1
            item.status = 1
            item.total_amt = item.productid.amount * item.quantity
            item.invoice.save(f"invoice_{item.id}.pdf", File(invoice_file), save=True)

        return redirect('payment_success')  # Replace with your own success URL

    return render(request, "payment.html", {'cartid': cartid})


def generate_invoice(cart_items, total_amount, user):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, y, "INVOICE")
    y -= 30

    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Customer: {user.username}")
    y -= 20
    p.drawString(50, y, f"Date: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
    y -= 40

    p.drawString(50, y, "Product")
    p.drawString(200, y, "Quantity")
    p.drawString(300, y, "Unit Price")
    p.drawString(400, y, "Total")
    y -= 20

    for item in cart_items:
        p.drawString(50, y, item.productid.name)
        p.drawString(200, y, str(item.quantity))
        p.drawString(300, y, str(item.productid.amount))
        total_price = item.productid.amount * item.quantity
        p.drawString(400, y, str(total_price))
        y -= 20
        if y < 100:
            p.showPage()
            y = height - 50

    y -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total Amount: ₹{total_amount}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


# def save_invoice_to_file(user, cart_items, amount, cartid):
#     invoice_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
#     os.makedirs(invoice_dir, exist_ok=True)

#     filename = f"invoice_{user.name}_{cartid}.pdf"
#     filepath = os.path.join(invoice_dir, filename)

#     p = canvas.Canvas(filepath, pagesize=A4)
#     p.setFont("Helvetica-Bold", 20)
#     p.drawString(200, 800, "Invoice")

#     p.setFont("Helvetica", 12)
#     p.drawString(50, 750, f"Customer Name: {user.name}")
#     p.drawString(50, 730, f"Email: {user.loginid.email}")

#     y = 710
#     for item in cart_items:
#         p.drawString(50, y, f"Product: {item.productid.name}")
#         p.drawString(50, y-20, f"Quantity: {item.quantity}")
#         p.drawString(50, y-40, f"Price per unit: Rs. {item.productid.amount}")
#         y -= 70  # move down for next product

#     p.drawString(50, y, f"Total Amount Paid: Rs. {amount}")
#     p.drawString(50, y-60, "Thank you for your purchase!")
#     p.showPage()
#     p.save()

#     return filepath

def listsupplierdelivers(request,id):
    deliver=Delivery.objects.all()
    a=request.GET.get('search')
    if a:
        deliver=Delivery.objects.filter(Q(name__icontains=a))
    return render(request,'supplierdeliverlist.html',{'deliver':deliver, 'id':id})  
def allotsupplierdeliver(request,id):
    deliver=request.session.get('delivery_id')
    if not deliver:
        messages.error(request,'You are not valid deliverboy,please login and try again')
        return redirect('loginindex')   
    a=get_object_or_404(Delivery,loginid=deliver)
    b=get_object_or_404(ReOrder,id=id)
    
    
    b.buystatus=3
    b.save()
    if Allotsupplierdelivery.objects.filter(deliverid=a,orderid=b):
        messages.error(request,'Already Assigned')
        return redirect('deliveryhome')
    else:
        Allotsupplierdelivery.objects.create(deliverid=a,orderid=b)
        return redirect('deliveryhome') 
# def supplierdeliverallotview(request):
#     a=request.session.get('delivery_id')
#     b=get_object_or_404(Delivery,loginid=a)
#     data=Allotsupplierdelivery.objects.filter(deliverid=b)
#     return render(request,'supplierdeliveryview.html',{'data':data})   

def supplierdeliveredstatus(request,id):
    a=request.session.get('delivery_id')
    b=get_object_or_404(Delivery,loginid=a)
    c=get_object_or_404(ReOrder,id=id)
    c.deliveredstatus = 1
    c.save()
    b.deliverstatus = 0
    b.save()
    return redirect('deliveryhome')

def allot(request,id):
    a=get_object_or_404(Addtocart,id=id)
    a.buystatus=2 # shop allot
    a.save()
    return redirect('shophomepage')

def allotorders(request):
    a=request.session.get('delivery_id')
   
    if not a:
        messages.error(request,'You are not a valid deliverboy,please login and try again')
        return redirect('loginindex')

    b=get_object_or_404(Delivery,loginid=a)
    data=Allotdelivery.objects.filter(deliverid=b)
    return render(request,'allotorders.html',{'data':data})
def onroute(request,id):
    delivery_id = request.session.get('delivery_id')
    delivery_person = Delivery.objects.get(loginid=delivery_id)
    delivery_person.deliverstatus = '0'
    a=get_object_or_404(Addtocart,id=id)
    a.buystatus=4
    a.save()
    return redirect('deliveryhome')
from django.shortcuts import render, get_object_or_404
from .models import Addtocart

def reorder(request,id):
    log=request.session.get('shop_id')
    if not log:
        messages.error(request,'You are not valid shop,please login and try again')
        return redirect('loginindex')   
    b=get_object_or_404(Product,id=id)
    shop=get_object_or_404(Shop,loginid=log)
    if request.method=='POST':
        form=ReOrderForm(request.POST)
        qua = int(request.POST.get('quantity'))
        amount=b.amount
        totalamount=qua*amount
        if form.is_valid():
                
                a=form.save(commit=False)
                a.shopid=shop
                a.productid=b
                a.amount=totalamount
                a.save()
                return redirect('reorderpayment',totalamount=totalamount,id=a.id)
    else:
        form=ReOrderForm()    
    return render(request,'reorderproduct.html',{'form':form,'b':b}) 
def reorderpayment(request,totalamount,id):
    shop=request.session.get('shop_id')
    a=get_object_or_404(Shop,loginid=shop)
    b=get_object_or_404(ReOrder,id=id)
    print(b)
    if request.method=='POST':
        form=PaymentForm(request.POST)
        if form.is_valid():
            c=form.save(commit=False)
            b.buystatus=1
            b.save()
            return redirect('shophomepage')
        else:
            form=PaymentForm() 
    return render(request,'reorderpayment.html',{'totalamount':totalamount})
def reorderallot(request,id):
    a=get_object_or_404(ReOrder,id=id)
    a.buystatus=2 
    a.save()
    return redirect('supplierhomepagenew')
def allotreorders(request):
    a=request.session.get('delivery_id')
    if not a:
        messages.error(request,'You are not valid deliverboy,please login and try again')
        return redirect('loginindex')
    b=get_object_or_404(Delivery,loginid=a)
    data=Allotsupplierdelivery.objects.filter(deliverid=b)
    return render(request,'allotreorders.html',{'data':data})
def reorderonroute(request,id):
    delivery = request.session.get('delivery_id')
    delivery_person = Delivery.objects.get(loginid=delivery)
    delivery_person.deliverstatus = '0'
    a=get_object_or_404(ReOrder,id=id)
    if a.buystatus != 4:
        product = a.productid
        if product:
            # Add quantity to product stock
            product.quantity += a.quantity  # 'stock' must be a field in your Product model
            product.save()
    a.buystatus=4
    a.save()
    return redirect('deliveryhome')
from django.shortcuts import render, get_object_or_404
from .models import ReOrder

def trackreorder(request, id):
    order = get_object_or_404(ReOrder, id=id)
    return render(request, 'reordertracking.html', {'buystatus': order.buystatus})
from django.shortcuts import render, get_object_or_404
from .models import Addtocart

def trackorder(request,id):
    order=get_object_or_404(Addtocart,id=id)
    return render(request,'track.html',{'buystatus': order.buystatus})
def addtocartorders(request):
    # Get user from session
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request,'You are not valid supplier,please login and try again')
        return redirect('loginindex')   
    user = get_object_or_404(User, loginid=user_id)

    # Get cart items with buystatus == 0 for this user
    cart_items = Addtocart.objects.filter(buystatus=0, loginid=user)

    # Sum the already-calculated 'amount' field from Addtocart
    total_amount = sum(item.total_amt for item in cart_items)

    return render(request, 'addtocartorders.html', {
        'order': cart_items,
        'total_amount': total_amount,
    })
def buy_selected_items(request):
   
    if not user_id:
        messages.error(request,'You are not a valid admin,please login and try again')
        return redirect('loginindex')
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        user = get_object_or_404(User, loginid=user_id)

        selected_ids = request.POST.getlist('selected_items')
        selected_items = Addtocart.objects.filter(pk__in=selected_ids, loginid=user, buystatus=0)
        total_amount = sum(item.total_amt for item in selected_items)

        return render(request, 'userpayment.html', {
            'items': selected_items,
            'total_amount': total_amount,  # ✅ Only selected items' total
            'selected_ids': selected_ids   # Send IDs for reference if needed
        })


# def userpayment(request,totalamount,id):
#     user=request.session.get('user_id')
#     a=get_object_or_404(User,loginid=user)
#     b=get_object_or_404(Addtocart,cartid=id)
#     print(b)
#     if request.method=='POST':
#         form=PaymentForm(request.POST)
#         if form.is_valid():
#             c=form.save(commit=False)
#             b.buystatus=1
#             b.save()
#             return redirect('userhomepage')
#         else:
#             form=PaymentForm() 
#     return render(request,'reorderpayment.html',{'totalamount':totalamount})


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Addtocart, User
from .forms import PaymentForm
from django.core.files import File
from django.conf import settings
import os

def userpayment(request, cartid):
    user_id = request.session.get('user_id')
    if not user_id:
        return HttpResponse("User not logged in", status=401)

    user = get_object_or_404(User, loginid=user_id)

    if request.method == 'POST':
        if 'selected_items' in request.POST:
            # STEP 1: User selected items from cart → show payment form
            selected_ids = request.POST.getlist('selected_items')
            request.session['selected_ids'] = selected_ids  # Save to session temporarily

            cart_items = Addtocart.objects.filter(pk__in=selected_ids, cartid=cartid, buystatus=0, loginid=user)
            total_amount = sum(item.total_amt or item.productid.amount * item.quantity for item in cart_items)

            form = PaymentForm()
            return render(request, 'userpayment.html', {
                'cart_items': cart_items,
                'total_amount': total_amount,
                'form': form,
                'cartid': cartid,
            })

        else:
            # STEP 2: Submitting the payment form
            selected_ids = request.session.get('selected_ids')
            if not selected_ids:
                return HttpResponse("No selected items in session", status=400)

            cart_items = Addtocart.objects.filter(pk__in=selected_ids, cartid=cartid, buystatus=0, loginid=user)
            total_amount = sum(item.total_amt or item.productid.amount * item.quantity for item in cart_items)

            form = PaymentForm(request.POST)
            if form.is_valid():
                payment = form.save(commit=False)
                payment.amount = total_amount
                payment.loginid = user
                payment.cart = cartid
                payment.save()

                for item in cart_items:
                    item.buystatus = 1
                    item.status = 1
                    item.total_amt = item.productid.amount * item.quantity

                    product = item.productid
                    if product.quantity >= item.quantity:
                        product.quantity -= item.quantity
                        product.save()
                    else:
                        return HttpResponse(f"Insufficient stock for product: {product.name}", status=400)

                    item.save()

                invoice_path = save_invoice_to_file(user, cart_items, total_amount, cartid)
                with open(invoice_path, 'rb') as f:
                    invoice_file = File(f)
                    for item in cart_items:
                        f.seek(0)
                        item.invoice.save(os.path.basename(invoice_path), invoice_file, save=True)

                # Clear session data
                del request.session['selected_ids']

                return render(request, 'payment_success.html', {
                    'invoice_url': settings.MEDIA_URL + 'invoices/' + os.path.basename(invoice_path)
                })

            else:
                return render(request, 'userpayment.html', {
                    'cart_items': cart_items,
                    'total_amount': total_amount,
                    'form': form,
                    'cartid': cartid,
                    'errors': form.errors,
                })

    else:
        return HttpResponse("Invalid access method", status=405)


def save_invoice_to_file(user, cart_items, amount, cartid):
    invoice_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(invoice_dir, exist_ok=True)

    filename = f"invoice_{user.name}_{cartid}.pdf"
    filepath = os.path.join(invoice_dir, filename)

    p = canvas.Canvas(filepath, pagesize=A4)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(230, 800, "INVOICE")

    p.setFont("Helvetica", 12)
    p.drawString(50, 770, f"Customer Name: {user.name}")
    p.drawString(50, 750, f"Email: {user.loginid.email}")
    p.drawString(50, 730, f"Cart ID: {cartid}")

    y = 700
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Product")
    p.drawString(250, y, "Quantity")
    p.drawString(350, y, "Unit Price")
    p.drawString(450, y, "Total")
    p.setFont("Helvetica", 12)
    y -= 20

    for item in cart_items:
        total = item.productid.amount * item.quantity
        p.drawString(50, y, item.productid.name)
        p.drawString(250, y, str(item.quantity))
        p.drawString(350, y, f"Rs. {item.productid.amount}")
        p.drawString(450, y, f"Rs. {total}")
        y -= 20

        if y < 100:
            p.showPage()
            y = 750

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"Total Amount Paid: Rs. {amount}")
    y -= 40
    p.drawString(50, y, "Thank you for your purchase!")

    p.showPage()
    p.save()

    return filepath


def deleteorderproduct(request,id):
    a=get_object_or_404(Addtocart,id=id)
    a.delete()
    return redirect('addtocartorders')



# sales report

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, F
from django.utils.dateparse import parse_date
import json
import pandas as pd
from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder
from .models import Addtocart

def sales_dashboard(request):
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    category = request.GET.get('category')

    sales_qs = Addtocart.objects.filter(buystatus=1)

    if from_date and to_date:
        sales_qs = sales_qs.filter(currentdate__date__range=[from_date, to_date])
    if category:
        sales_qs = sales_qs.filter(productid__category__icontains=category)

    # Daily Sales
    daily_sales = sales_qs.extra({'date': "DATE(currentdate)"}).values('date') \
        .annotate(total_sales=Sum('total_amt')) \
        .order_by('date')

    # Monthly Revenue
    monthly_revenue = sales_qs.annotate(month=F('currentdate__month')) \
        .values('month', 'productid__name') \
        .annotate(revenue=Sum('total_amt')) \
        .order_by('month')

    # Top Products
    top_products = sales_qs.values('productid__name') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold')[:5]

    # Inventory Turnover
    total_sales_qty = sales_qs.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_inventory = Addtocart.objects.aggregate(Sum('quantity'))['quantity__sum'] or 1
    turnover_rate = round(total_sales_qty / total_inventory, 2)
    total_revenue = sales_qs.aggregate(Sum('total_amt'))['total_amt__sum'] or 0


    context = {
        'daily_sales': json.dumps(list(daily_sales), cls=DjangoJSONEncoder),
        'monthly_revenue': json.dumps(list(monthly_revenue),    cls=DjangoJSONEncoder),
        'top_products': top_products,
        'turnover_rate': turnover_rate,
        'from': from_date,
        'to': to_date,
        'category': category,
        'total_revenue' : total_revenue
    }
    return render(request, 'sales_report.html', context)

def export_sales_excel(request):
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    category = request.GET.get('category')

    sales_qs = Addtocart.objects.filter(buystatus=1)

    if from_date and to_date:
        sales_qs = sales_qs.filter(currentdate__date__range=[from_date, to_date])
    if category:
        sales_qs = sales_qs.filter(productid__category__icontains=category)

    qs = sales_qs.values(
        product_name=F('productid__name'),
        user_name=F('loginid__name'),
        quantity=F('quantity'),
        total_amt=F('total_amt'),
        date=F('currentdate')
    )
    df = pd.DataFrame(list(qs))
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="filtered_sales_report.xlsx"'
    df.to_excel(response, index=False)
    return response


# inventory predeection

# import pandas as pd
# from datetime import timedelta
# from django.shortcuts import render
# from sklearn.linear_model import LinearRegression
# from .models import Addtocart

# def inventory_forecast(request):
#     confirmed_orders = Addtocart.objects.filter(buystatus=1, cancelstatus=0).values('currentdate', 'productid__productname', 'quantity')
#     df = pd.DataFrame(confirmed_orders)

#     if df.empty:
#         return render(request, 'inventory_forecast.html', {'forecast_results': []})

#     df['currentdate'] = pd.to_datetime(df['currentdate'])
#     df['currentdate'] = df['currentdate'].dt.date

#     forecast_results = []

#     for product in df['productid__productname'].unique():
#         product_df = df[df['productid__productname'] == product]
#         product_df = product_df.groupby('currentdate').agg({'quantity': 'sum'}).reset_index()
#         product_df['date_num'] = (pd.to_datetime(product_df['currentdate']) - pd.to_datetime(product_df['currentdate'].min())).dt.days

#         if len(product_df) >= 2:
#             model = LinearRegression()
#             model.fit(product_df[['date_num']], product_df['quantity'])

#             future_days = 30
#             last_day_num = product_df['date_num'].max()
#             future_dates = [last_day_num + i for i in range(1, future_days + 1)]
#             predicted_qty = model.predict([[d] for d in future_dates])
#             forecast_dates = [product_df['currentdate'].max() + timedelta(days=i) for i in range(1, future_days + 1)]

#             forecast_results.append({
#                 'product': product,
#                 'forecast': list(zip(forecast_dates, predicted_qty))
#             })

#     return render(request, 'inventory_forecast.html', {'forecast_results': forecast_results})

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Sum, F
from django.utils.dateparse import parse_date
import json
import pandas as pd
from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder
from .models import Addtocart, Product, Shop, Login

def shop_sales_dashboard(request):
    # Ensure user is logged in
    login_id = request.session.get('shop_id')  # Adjust according to your session key
    if not login_id:
        return HttpResponse("Unauthorized", status=401)

    # Get filters
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    category = request.GET.get('category')

    # Filter products that belong to this shop owner
    shop_products = Product.objects.filter(loginid=login_id).values_list('id', flat=True)

    # Filter Addtocart entries for those products only
    sales_qs = Addtocart.objects.filter(buystatus=1, productid__in=shop_products)

    if from_date and to_date:
        sales_qs = sales_qs.filter(currentdate__date__range=[from_date, to_date])
    if category:
        sales_qs = sales_qs.filter(productid__category__icontains=category)

    # Daily Sales
    daily_sales = sales_qs.extra({'date': "DATE(currentdate)"}).values('date') \
        .annotate(total_sales=Sum('total_amt')) \
        .order_by('date')

    # Monthly Revenue
    monthly_revenue = sales_qs.annotate(month=F('currentdate__month')) \
        .values('month', 'productid__name') \
        .annotate(revenue=Sum('total_amt')) \
        .order_by('month')

    # Top Products
    top_products = sales_qs.values('productid__name') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold')[:5]

    # Inventory Turnover (shop-specific)
    total_sales_qty = sales_qs.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_inventory = Product.objects.filter(id__in=shop_products).aggregate(Sum('quantity'))['quantity__sum'] or 1
    turnover_rate = round(total_sales_qty / total_inventory, 2) #divison
    total_revenue = sales_qs.aggregate(Sum('total_amt'))['total_amt__sum'] or 0

    context = {
        'daily_sales': json.dumps(list(daily_sales), cls=DjangoJSONEncoder),
        'monthly_revenue': json.dumps(list(monthly_revenue), cls=DjangoJSONEncoder),
        'top_products': top_products,
        'turnover_rate': turnover_rate,
        'from': from_date,
        'to': to_date,
        'category': category,
        'total_revenue': total_revenue,
        'shop_view': True  # You can use this in template to differentiate views
    }
    return render(request, 'shop_sales_report.html', context)

from django.http import JsonResponse

def shop_sales_data_api(request):
    login_id = request.session.get('shop_id')
    if not login_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    shop_products = Product.objects.filter(loginid=login_id).values_list('id', flat=True)
    sales_qs = Addtocart.objects.filter(buystatus=1, productid__in=shop_products)

    # Daily Sales
    daily_sales = sales_qs.extra({'date': "DATE(currentdate)"}).values('date') \
        .annotate(total_sales=Sum('total_amt')).order_by('date')

    # Monthly Revenue
    monthly_revenue = sales_qs.annotate(month=F('currentdate__month')) \
        .values('month', 'productid__name') \
        .annotate(revenue=Sum('total_amt')).order_by('month')

    # Top Products
    top_products = sales_qs.values('productid__name') \
        .annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:5]

    # Inventory Turnover
    total_sales_qty = sales_qs.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_inventory = Product.objects.filter(id__in=shop_products).aggregate(Sum('quantity'))['quantity__sum'] or 1
    turnover_rate = round(total_sales_qty / total_inventory, 2)
    total_revenue = sales_qs.aggregate(Sum('total_amt'))['total_amt__sum'] or 0

    return JsonResponse({
        'daily_sales': list(daily_sales),
        'monthly_revenue': list(monthly_revenue),
        'top_products': list(top_products),
        'turnover_rate': turnover_rate,
        'total_revenue': total_revenue
    }, safe=False)






import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from django.shortcuts import render
from django.db.models import Sum
from Track1.models import Addtocart, Product

def forecast_inventory_demand(request):
    selected_product = request.GET.get('product', '')
    forecast_data = []

    product_names = Product.objects.values_list('name', flat=True).distinct()

    if selected_product:
        sales_data = (
            Addtocart.objects.filter(productid__name=selected_product, buystatus=1)
            .values('currentdate')
            .annotate(total_qty=Sum('quantity'))
            .order_by('currentdate')
        )

        if sales_data:
            df = pd.DataFrame(sales_data)
            df['currentdate'] = pd.to_datetime(df['currentdate'])
            df = df.groupby(df['currentdate'].dt.date).sum().reset_index()
            df.rename(columns={'currentdate': 'Date', 'total_qty': 'Quantity'}, inplace=True)

            df['Date'] = pd.to_datetime(df['Date'])
            df['DayIndex'] = (df['Date'] - df['Date'].min()).dt.days

            model = LinearRegression()
            model.fit(df[['DayIndex']], df['Quantity'])

            future_dates = [df['Date'].max() + timedelta(days=i) for i in range(1, 31)]
            future_day_indices = [(date - df['Date'].min()).days for date in future_dates]

            forecast = model.predict(np.array(future_day_indices).reshape(-1, 1))
            forecast_df = pd.DataFrame({
                "Date": future_dates,
                "Predicted_Quantity": forecast.astype(int)
            })

            forecast_data = forecast_df.to_dict(orient='records')

    return render(request, 'inventory_forecast.html', {
        'products': product_names,
        'selected_product': selected_product,
        'forecast': forecast_data
    })



from django.shortcuts import render
from django.db.models import Sum
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from .models import Addtocart, Product

def predict_inventory_demand(request):
    login_id = request.session.get('shop_id')
    if not login_id:
        return render(request, 'unauthorized.html')

    shop_products = Product.objects.filter(loginid=login_id)
    prediction_results = []
    chart_labels = []
    chart_data = []

    for product in shop_products:
        sales_qs = Addtocart.objects.filter(
            productid=product, buystatus=1
        ).extra({'sale_date': "DATE(currentdate)"}).values('sale_date') \
         .annotate(total_quantity=Sum('quantity')).order_by('sale_date')

        if len(sales_qs) < 2:
            continue

        df = pd.DataFrame(sales_qs)
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df['days'] = (df['sale_date'] - df['sale_date'].min()).dt.days
        X = df[['days']].values
        y = df['total_quantity'].values

        model = LinearRegression()
        model.fit(X, y)

        future_days = np.array([[df['days'].max() + i] for i in range(1, 31)])
        future_qty = model.predict(future_days)
        predicted_qty = max(int(np.sum(future_qty)), 0)

        prediction_results.append({
            'product_name': product.name,
            'category': product.category,
            'predicted_quantity': predicted_qty
        })

        # Prepare for Chart
        chart_labels.append(product.name)
        chart_data.append(predicted_qty)

    context = {
        'predictions': prediction_results,
        'chart_labels': chart_labels,
        'chart_data': chart_data
    }
    return render(request, 'inventory_forecast.html', context)

  



    # for generating sales data
def generate_sales_data(entries=200):             
    import random
    from datetime import datetime, timedelta
    from django.utils import timezone

    # Replace 'yourapp' with the actual app name
    from .models import Addtocart, Product, User

    # Define the fixed date range: Jan 1 – Jun 30, 2025
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 6, 30)
    delta_days = (end_date - start_date).days

    # Fetch users and products
    users = list(User.objects.all())
    products = list(Product.objects.all())

    if not users or not products:
        print("❌ No users or products found. Please add them first.")
    else:
        NUM_ENTRIES = 200  # Total entries to insert

        for _ in range(NUM_ENTRIES):
            product = random.choice(products)
            user = random.choice(users)
            quantity = random.randint(1, 5)
            random_day_offset = random.randint(0, delta_days)
            sale_date = start_date + timedelta(days=random_day_offset)
            total_price = product.amount * quantity

            Addtocart.objects.create(
                productid=product,
                loginid=user,
                quantity=quantity,
                currentdate=sale_date,
                buystatus=1,
                status=1,
                deliveredstatus=1,
                total_amt=total_price,
                cartid=str(random.randint(10000, 99999))
            )

    print(f"✅ Successfully inserted {NUM_ENTRIES} sales between Jan–Jun 2025.")
    

