from datetime import datetime
from os import error
from django.http import request
from django.shortcuts import redirect, render
from django.urls.base import reverse
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uuid
from oauth2client.client import Error
import pyrebase

import json
from .decorators import login_session_required

# Create your views here.


cred = credentials.Certificate(
    "fortec-a7359-firebase-adminsdk-7mldo-40b32c1cf6.json")

firebaseConfig = {
    'apiKey': "AIzaSyAIYbpmmvXfuExHgUOuQxKvOVVl7Lx4qCs",
    'authDomain': "fortec-a7359.firebaseapp.com",
    'databaseURL': "https://fortec-a7359-default-rtdb.firebaseio.com",
    'projectId': "fortec-a7359",
    'storageBucket': "fortec-a7359.appspot.com",
    'messagingSenderId': "870315177780",
    'appId': "1:870315177780:web:a18fb35998b21a55aa9761",
    'measurementId': "G-6S9M7LCZGV"

}
firebase_admin.initialize_app(cred)
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()
database = firebase.database()
auth = firebase.auth()

db = firestore.client()


def index(request):
    docsMostSold = db.collection('products').order_by(
        'soldNo').limit_to_last(8).get()
    passed_values_mostSold = [doc.to_dict() for doc in docsMostSold]
    docsNewProducts = db.collection('products').order_by(
        'date').limit_to_last(8).get()
    for x in docsMostSold:
        print(x)
    passed_values_NewProducts = [doc.to_dict() for doc in docsNewProducts]

    return render(request, 'index.html', {'mostSold': passed_values_mostSold, 'newProducts': passed_values_NewProducts})


def signIn(request):
    msg = ''
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            auth.sign_in_with_email_and_password(email, password)
            userGet = db.collection('users').document(email)
            usersdocs = userGet.get().to_dict()
            request.session['name'] = usersdocs['firstName'] + ' '
            + usersdocs.lastName
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
            user = auth.create_user_with_email_and_password(email, password)
            new_doc_ref = db.collection('users').document(email)
            data = {
                'firstName': firstName,
                'lastName': lastName,
                'Email': email,
                'total': 0,
                'phone': phone,
                'uid': user,
                'city': '',
                'cart': [],
            }
            new_doc_ref.set(data),
            session_id = user['idToken']
            request.session['email'] = email
            request.session['name'] = firstName + ' '+lastName
            request.session['uid'] = str(session_id)
            return redirect('index')
        except Exception as e:
            print(e)
            msg = "Your password should be at least 6 char!"
    else:
        print("GET")
    return render(request, 'signUp.html', {'msg': msg})


def logout(request):
    del request.session['name']
    del request.session['uid']
    del request.session['email']
    return render(request, 'signIn.html')


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

            cart = usersdocs['cart']
            cart.append(cartItem)
            print(cart)
            userGet.update({
                'cart': cart,
                'total': total
            })
            return redirect('checkout')
        except Exception as e:
            print(str(e))
    else:
        print("GETTING")

    return render(request, 'productDetails.html', {'ProductsGet': doc})


'''

@login_session_required(login_url='contacts')
def checkout(request):
    Email = request.session['Email']
    OrderNote = request.POST.get('OrderNote')
    userGet = db.collection('users').document(Email)
    usersdocs = userGet.get().to_dict()
    print(Email)
    if request.method == 'POST':
        try:
            firstName = usersdocs['firstName']
            lastName = usersdocs['lastName']
            PhoneNumber = usersdocs['PhoneNumber']
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
    return render(request, 'checkout.html', {'usersdocs': usersdocs})


@login_session_required(login_url='contacts')
def thankyou(request):
    return render(request, 'thankyou.html')
 '''
# /home/XEatsNew/X-Eats-Website
