from datetime import datetime
from os import error, name
from django.http import request
from django.shortcuts import redirect, render
from django.urls.base import reverse
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid
from oauth2client.client import Error
from pyasn1.type.univ import Null
import pyrebase

import json
from .decorators import login_session_required

# Create your views here.


cred = credentials.Certificate(
    "trutech-464cb-firebase-adminsdk-4v8do-68464c2077.json")

firebaseConfig = {
    'apiKey': "AIzaSyBuY3CpF5V6Kceyr5QelfTRocZyIVhvyhw",
    'authDomain': "trutech-464cb.firebaseapp.com",
    'databaseURL': "https://trutech-464cb-default-rtdb.firebaseio.com",
    'projectId': "trutech-464cb",
    'storageBucket': "trutech-464cb.appspot.com",
    'messagingSenderId': "756831507071",
    'appId': "1:756831507071:web:282ed47a41c197cfc4e54a",
    'measurementId': "G-7D8TL4JSLW"

}
firebase_admin.initialize_app(cred)
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()
database = firebase.database()
auth = firebase.auth()

db = firestore.client()


def cartNoFunction(request):
    if (request.session.keys()):
        cart = ((db.collection('users').document(
            request.session['email']).get()).to_dict()['cart'])
        cartNo = 0
        for product in cart:
            cartNo += product['Quantity']

        return(cartNo)


def index(request):
    docsMostSold = db.collection('products').order_by(
        'soldNo').limit_to_last(8).get()
    passed_values_mostSold = [doc.to_dict() for doc in docsMostSold]
    docsNewProducts = db.collection('products').order_by(
        'date').limit_to_last(8).get()

    passed_values_NewProducts = [doc.to_dict() for doc in docsNewProducts]

    return render(request, 'index.html', {'mostSold': passed_values_mostSold, 'newProducts': passed_values_NewProducts, 'cartNo': cartNoFunction(request)})


def signIn(request):
    msg = ''
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = auth.sign_in_with_email_and_password(email, password)
            userGet = db.collection('users').document(email)
            usersdocs = userGet.get().to_dict()
            request.session['name'] = usersdocs['firstName']
            request.session['email'] = email
            return redirect('index')
        except Exception as e:
            print(str(e))
            msg = "Wrong email or password!"
    else:
        print("GET")
    return render(request, 'signIn.html', {'msg': msg})


def signUp(request):
    msg = ''
    if request.method == 'POST':
        try:

            firstName = request.POST.get('firstName')
            lastName = request.POST.get('lastName')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirmpassword = request.POST.get('confirmpassword')
            if password == confirmpassword:

                user = auth.create_user_with_email_and_password(
                    email, password)
                new_doc_ref = db.collection('users').document(email)
                data = {
                    'firstName': firstName,
                    'lastName': lastName,
                    'Email': email,
                    'total': 0,
                    'phoneNumber': phone,
                    'id': user,
                    'city': '',
                    'cart': [],
                }
                new_doc_ref.set(data),
                session_id = user['idToken']
                request.session['email'] = email
                request.session['name'] = firstName + ' '+lastName

                return redirect('index')
            else:
                msg = "Password and confirm password doesn't match!"
        except Exception as e:
            print(e)
            if('EXISTS' in str(e)):
                msg = 'You email ecxists'
            else:
                msg = "Your password should be at least 6 char!"
    else:
        print("GET")
    return render(request, 'signUp.html', {'msg': msg})


def logout(request):
    del request.session['name']
    del request.session['email']
    return render(request, 'signIn.html', {'cartNo': cartNoFunction(request)})


def categories(request):
    categories = [
        {
            'name': 'mostsold',
            'img': 'any.png'
        },
        {
            'name': 'Second Category',
            'img': 'any.png'
        },
        {
            'name': 'Third Category',
            'img': 'any.png'
        },
        {
            'name': 'Fourth Category',
            'img': 'any.png'
        },

    ]
    return render(request, 'categories.html', {'categories': categories, 'cartNo': cartNoFunction(request)})


def products(request, category=''):
    if (len(category)):
        docs = db.collection('products').where(
            'category', '==', category).get()
    else:
        docs = db.collection('products').get()
    result = [doc.to_dict() for doc in docs]
    return render(request, 'shop.html', {'docs': result, 'cartNo': cartNoFunction(request)})


def cart(request):
    if (len(request.session.keys()) > 0):
        print(request.session['email'])
        doc = db.collection('users').document(request.session['email']).get()
        cart = doc.to_dict()
        print(cart)
        return render(request, 'cart.html', {'cart': cart, 'cartNo': cartNoFunction(request)})

    else:
        return redirect('login')


def addProductToCart(request, id):
    email = request.session['email']
    user = db.collection('users').document(
        email).get().to_dict()
    cart = user['cart']
    for i in range(len(cart)):
        if (cart[i]['ProductID'] == id):
            cart[i]['Quantity'] += 1

            db.collection('users').document(email).update({
                'total': user['total'] + cart[i]['Price'],
                'cart': cart
            })
            return redirect('cart')


def removeProductFromCart(request, id):
    email = request.session['email']
    user = db.collection('users').document(
        email).get().to_dict()
    cart = user['cart']
    for i in range(len(cart)):
        if (cart[i]['ProductID'] == id):

            total = user['total'] - cart[i]['Price'] * cart[i]['Quantity']
            cart.pop(i)
            db.collection('users').document(email).update({
                'total': total,
                'cart': cart
            })
            return redirect('cart')


''' def contacts(request):
    if request.method == 'POST':
        try:
            firstName = request.POST.get('firstName')
            lastName = request.POST.get('lastName')
            Email = request.POST.get('Email')
            # Password = request.POST.get('Password')
            PhoneNumber = request.POST.get('PhoneNumber')
            old_auth = firebase.auth()
            XEats_User = old_auth.create_user_with_email_and_password(
                Email, 'Password')
            user = old_auth.refresh(XEats_User['refreshToken'])
            ID = uuid.uuid4()
            request.session['Email'] = Email
            new_doc_ref = db.collection('users').document(Email)
            new_doc_ref.set({
                'firstName': firstName,
                'lastName': lastName,
                'Email & ID': Email,
                'total': 0,
                'PhoneNumber': PhoneNumber,
                'cart': [],
            }),

            return redirect('shop')
        except Exception as e:
            print(str(e))
    else:
        print("GETTING")
    return render(request, 'contacts.html')
 '''
'''
@login_session_required(login_url='contacts')
def shop(request,):
    from google.cloud import firestore
    docs = db.collection(u'products').stream()
    auth = firebase.auth()
    passed_values = [doc.to_dict() for doc in docs]
    Email = request.session['Email']

    print(Email)


    # request.session['Email'] = Email

    for i in passed_values:
        id = i['id']
        productName = i['name']
        price = i['price']
        category = i['category']

    if request.method == 'POST':
        redirect('productDetails', {'id': id, })
    return render(request, 'shop.html', {
        "docs": passed_values,
    })

'''
# @login_session_required(login_url='contacts')


def productDetails(request, id):
    ProductsGet = db.collection('products').document(str(id))
    doc = ProductsGet.get().to_dict()

    if request.method == 'POST':
        try:
            if len(request.session.keys()) > 0:
                email = request.session['email']
                userGet = db.collection('users').document(email)
                usersdocs = userGet.get().to_dict()
                Quantity = request.POST.get('Quantity')
                request.session['email'] = email
                cartItem = {
                    'ProductName': doc['name'],
                    'Quantity': int(Quantity),
                    'Price': doc['price'],
                    'Category': doc['category'],
                    'ProductID': doc['id']
                }

                totalPrice = int(Quantity) * doc['price']
                total = usersdocs['total'] + totalPrice
                if not any(d['ProductName'] == doc['name'] for d in usersdocs['cart']):

                    cart = usersdocs['cart']
                    cart.append(cartItem)
                else:
                    for d in range(len(usersdocs['cart'])):
                        if (usersdocs['cart'][d]['ProductName'] == cartItem['ProductName']):
                            usersdocs['cart'][d]['Quantity'] += 1
                            cart = usersdocs['cart']
                            break
                userGet.update({
                    'cart': cart,
                    'total': total
                })
                return redirect('cart')
            else:
                return redirect('signin')
        except Exception as e:
            print(str(e))
    else:
        print("GETTING")

    return render(request, 'productDetails.html', {'ProductsGet': doc})


def checkout(request):
    Email = request.session['email']
    OrderNote = request.POST.get('OrderNote')
    userGet = db.collection('users').document(Email)
    usersdocs = userGet.get().to_dict()
    if request.method == 'POST':
        try:
            firstName = usersdocs['firstName']
            lastName = usersdocs['lastName']
            PhoneNumber = usersdocs['phoneNumber']
            cart = usersdocs['cart']
            total = usersdocs['total']
            ID = uuid.uuid4()
            new_doc_ref = db.collection('orders').document(str(ID))
            new_doc_ref.set({
                'firstName': firstName,
                'lastName': lastName,
                'Email': Email,
                'price': total + 5,
                'PhoneNumber': PhoneNumber,
                'OrderNote': OrderNote,
                'cart': cart,
                'Paid': False,
                'CreatedAt': datetime.now()
            }),
            userGet.update({
                'cart': [],
                'total': 0
            })
            return redirect('thankyou')
        except Exception as e:
            print(str(e))
    else:
        print("GETTING")
    return render(request, 'checkout.html', {'usersdocs': usersdocs, 'cartNo': cartNoFunction(request)})


def thankyou(request):
    return render(request, 'thankyou.html')
