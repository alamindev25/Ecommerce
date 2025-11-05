from django.shortcuts import render
from . models import Customer, Product, Cart, OrderPlaced
from django.views import View
from.forms import CustomerRegistrationForm
from django.contrib import messages
# Create your views here.
class ProductView(View):
 def get(self, request):
  gentspants = Product.objects.filter(category='GP')
  sares = Product.objects.filter(category='S')
  borkhs = Product.objects.filter(category='BK')
  lehengas=Product.objects.filter(category='L')
  babyfashions = Product.objects.filter(category='BF')
  return render(request, 'Shop/home.html', {'gentspants':gentspants, 'sares':sares,'borkhs':borkhs,'lehengas':lehengas,'babyfashions':babyfashions})

#def product_detail(request):
# return render(request, 'Shop/productdetail.html')

class ProductDetail(View):
 def get(self,request,pk):
  product=Product.objects.get(pk=pk)
  return render (request,'Shop/productdetail.html',{'product':product})
  
 

def add_to_cart(request):
 return render(request, 'Shop/addtocart.html')

def buy_now(request):
 return render(request, 'Shop/buynow.html')

def profile(request):
 return render(request, 'Shop/profile.html')

def address(request):
 return render(request, 'Shop/address.html')

def orders(request):
 return render(request, 'Shop/orders.html')

def change_password(request):
 return render(request, 'Shop/changepassword.html')

def lehenga(request,data=None):
 if data==None:
  lehengas=Product.objects.filter(category='L')
 elif data=="pakija" or data=="ponnoala":
  lehengas=Product.objects.filter(category='L').filter(brand=data)
 elif data=="below":
  lehengas=Product.objects.filter(category='L').filter(discounted_price__lt=2000)
 elif data=="above":
  lehengas=Product.objects.filter(category='L').filter(discounted_price__gt=2000)
 return render(request, 'Shop/lehenga.html',{'lehengas':lehengas})

#def login(request):
     #return render(request, 'Shop/login.html')

#def customerregistration(request):
 #return render(request, 'Shop/customerregistration.html')
class CustomerRegistrationView(View):
 def get(self,request):
  form=CustomerRegistrationForm()
  return render(request, 'Shop/customerregistration.html',{'form':form})
 def post(self, request):
  form=CustomerRegistrationForm(request.POST)
  if form.is_valid():
   messages.success(request,'Congratulations registration successfully done')
   form.save()
   return render(request, 'Shop/customerregistration.html',{'form':form})
  else:
   return render(request, 'Shop/customerregistration.html',{'form':form})
  
def profile(request):
 return render(request, 'Shop/profile.html')
   
def checkout(request):
 
 return render(request, 'Shop/checkout.html')
