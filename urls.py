from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('adminindex',views.adminindex,name='adminindex'),
    path('userindex',views.userindex,name='userindex'),
    path('loginindex',views.loginindex,name='loginindex'),
    path('shopregistration',views.shopregistration,name='shopregistration'),
    path('userregistration',views.userregistration,name='userregistration'),
    path('adminshop',views.adminshop,name='adminshop'),
    path('adminuser',views.adminuser,name='adminuser'),
    path('shophomepage',views.shophomepage,name='shophomepage'),
    path('userhomepage',views.userhomepage,name='userhomepage'),
    path('userprofile',views.userprofile,name='userprofile'),
    path('shopprofile',views.shopprofile,name='shopprofile'),
    path('productdetail',views.productdetail,name='productdetail'),
    path('viewproduct',views.viewproduct,name='viewproduct'),
    path('editproduct/<int:id>',views.editproduct,name='editproduct'),
    path('deleteproduct/<int:id>',views.deleteproduct,name='deleteproduct'),
    path('listproduct',views.listproduct,name='listproduct'),
    path('addtocart/<int:id>',views.addtocart,name='addtocart'),
    path('userview',views.userview,name='userview'),
    path('userdelete/<int:id>',views.userdelete,name='userdelete'),
    path('payment/<int:id>/<int:amount>',views.make_payment,name='payment'),
    path('userproductview',views.userproductview,name='userproductview'),
    path('shopproductview',views.shopproductview,name='shopproductview'),
    path('cancelstatus/<int:id>',views.cancelstatus,name='cancelstatus'),
    path('refundpayment<int:id>',views.refundpayment,name='refundpayment'),
    path('supplierregistration',views.supplierregistration,name='supplierregistration'),
    path('adminsupplier',views.adminsupplier,name='adminsupplier'),
    path('supplierhomepagenew',views.supplierhomepagenew,name='supplierhomepagenew'),
    path('supplierprofile',views.supplierprofile,name='supplierprofile'),
    path('listsuppliers',views.listsuppliers,name='listsuppliers'),
    
    path('supplierview',views.supplierview,name='supplierview'),
    path('shopreorderview',views.shopreorderview,name='shopreorderview'),
    path('reordercancelstatus/<int:id>',views.reordercancelstatus,name='reordercancelstatus'),
    # path('editreorder/<int:id>',views.editreorder,name='editreorder'),
    # path('deletereorderproduct/<int:id>',views.deletereorderproduct,name='deletereorderproduct'),
    path('salesdetails',views.salesdetails,name='salesdetails'),
    # path('index',views.index,name='index'),
    path('logoutview',views.logoutview,name='logoutview'),
    path('shopapprove/<int:id>',views.shopapprove,name='shopapprove'),
    path('shopreject/<int:id>',views.shopreject,name='shopreject'),
    path('supplierapprove/<int:id>',views.supplierapprove,name='supplierapprove'),
    path('supplierreject/<int:id>',views.supplierreject,name='supplierreject'),
    path('deliveryregistration',views.deliveryregistration,name='deliveryregistration'),
    path('deliveryhome',views.deliveryhome,name='deliveryhome'),
    path('deliveryprofile',views.deliveryprofile,name='deliveryprofile'),
    path('admindeliver',views.admindeliver,name='admindeliver'),
    path('listdelivers',views.listdelivers,name='listdelivers'),
    path('listsupplierdeliver',views.listsupplierdeliver,name='listsupplierdeliver'),
    path('allotdeliver/<int:id>',views.allotdeliver,name='allotdeliver'),
    path('deliverallotview',views.deliverallotview,name='deliverallotview'),
    path('deliveredstatus_product/<int:id>/', views.deliveredstatus_product, name='deliveredstatus_product'),

    path('deliverapprove/<int:id>',views.deliverapprove,name='deliverapprove'),
    path('deliverreject/<int:id>',views.deliverreject,name='deliverreject'),
    path('payment/userhomepage', views.userhomepage, name='userhomepage'),
    path('listsupplierdelivers/<int:id>',views.listsupplierdelivers,name='listsupplierdelivers'),
    path('allotsupplierdeliver/<int:id>',views.allotsupplierdeliver,name='allotsupplierdeliver'),
    # path('supplierdeliverallotview',views.supplierdeliverallotview,name='supplierdeliverallotview'),
    path('supplierdeliveredstatus/<int:id>',views.supplierdeliveredstatus,name='supplierdeliveredstatus'),
    path('allot/<int:id>',views.allot,name='allot'),
    path('allotorders',views.allotorders,name='allotorders'),
    path('onroute/<int:id>',views.onroute,name='onroute'),
    # path('track/<int:id>/<int:status>/', views.track, name='track'),
    path('reorder/<int:id>',views.reorder,name='reorder'),
    path('reorderpayment<int:totalamount>/<int:id>',views.reorderpayment,name='reorderpayment'),
    path('reorderallot/<int:id>',views.reorderallot,name='reorderallot'),
    path('allotreorders',views.allotreorders,name='allotreorders'),
    path('reorderonroute/<int:id>',views.reorderonroute,name='reorderonroute'),
    path('trackreorder/<int:id>',views.trackreorder,name='trackreoder'),
    path('trackorder/<int:id>',views.trackorder,name='trackorder'),
    path('addtocartorders',views.addtocartorders,name='addtocartorders'),
    path('buyselected/', views.buy_selected_items, name='buyselected'),

    path('userpayment/<str:cartid>',views.userpayment,name='userpayment'),
    path('deleteorderproduct/<int:id>',views.deleteorderproduct,name='deleteorderproduct'),
    
    

    # sales report
    path('sales-dashboard/', views.sales_dashboard, name='sales_dashboard'), #admin sales dashboard
    path('export-sales-excel/', views.export_sales_excel, name='export_sales_excel'),
    path('dev/generate-sales/', views.generate_sales_data),
    path('inventory_forecast/', views.predict_inventory_demand, name='inventory_forecast'), #predict 
    path('shop_sales_report/', views.shop_sales_dashboard, name='shop_sales_dashboard'), #shop data
    path('api/shop_sales_data/', views.shop_sales_data_api, name='shop_sales_data_api'),






    
    









    
    
    
    
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)