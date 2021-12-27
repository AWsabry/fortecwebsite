from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('signin', views.signIn,  name='signin'),
    path('signup', views.signUp,  name='signup'),
    path('logout', views.logout,  name='logout'),
    path('categories', views.categories,  name='categories'),
    path('cart', views.cart,  name='cart'),
    path('checkout', views.checkout,  name='checkout'),
    path('thankyou', views.thankyou,  name='thankyou'),
    path('productadd<id>', views.addProductToCart,  name='addProductToCart'),
    path('productremove<id>', views.removeProductFromCart,
         name='removeProductFromCart'),

    path('products',
         views.products,  name='products'),
    path('products<category>',
         views.products,  name='productsByCategory'),
    path('product<id>', views.productDetails,  name='productdetails'),

]
''' path('shop', views.shop, name='shop'),
    path('thankyou', views.thankyou, name='thankyou'),
    path('checkout', views.checkout, name='checkout'),
    path('contacts', views.contacts, name='contacts'),
    path('<int:id>', views.productDetails, name='productDetails')
 '''
