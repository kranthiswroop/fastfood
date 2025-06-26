from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import CustomLogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    path('checkout/', views.checkout, name='checkout'),
    path('about/', views.about, name='about'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # Cart & Order
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('place-order/', views.place_order, name='place_order'),
    path('my-orders/', views.order_history, name='order_history'),

    # Chatbot
    path('chatbot/', views.chatbot_response, name='chatbot'),
]
