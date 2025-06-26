from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import MenuItem, Category, Order, OrderItem

def home(request):
    return render(request, 'home.html')

def menu(request):
    items = MenuItem.objects.all()
    search_query = request.GET.get('search')
    category = request.GET.get('category')

    if search_query:
        items = items.filter(name__icontains=search_query)
    if category:
        items = items.filter(category=category)

    return render(request, 'menu.html', {'menu_items': items})

def about(request):
    return render(request, 'about.html')

# def checkout(request):
#     request.session['cart'] = []
#     return render(request, 'checkout.html')
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    items = []
    total_amount = 0

    for item_id, quantity in cart.items():
        try:
            menu_item = MenuItem.objects.get(id=item_id)
            total_amount += int(menu_item.price * quantity * 100)  # amount in paise
            items.append({'item': menu_item, 'quantity': quantity})
        except MenuItem.DoesNotExist:
            continue

    if total_amount == 0:
        return redirect('menu')

    # Create Stripe PaymentIntent
    intent = stripe.PaymentIntent.create(
        amount=total_amount,
        currency='inr',
        metadata={'user_id': request.user.id}
    )

    return render(request, 'checkout.html', {
        'items': items,
        'total': total_amount / 100,
        'client_secret': intent.client_secret,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_TEST_PUBLIC_KEY
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def chatbot_response(request):
    user_msg = request.GET.get('msg', '').lower()
    if 'menu' in user_msg or 'food' in user_msg:
        bot_msg = "You can view our full menu by clicking 'Menu' in the navigation bar."
    elif 'order' in user_msg:
        bot_msg = "To place an order, just add items to your cart and click 'Checkout'."
    elif 'special' in user_msg:
        bot_msg = "Today's special is Spicy Paneer Pizza 🍕🔥!"
    elif 'hello' in user_msg or 'hi' in user_msg:
        bot_msg = "Hello! How can I help you today?"
    else:
        bot_msg = "I'm not sure about that. Try asking about menu or ordering."
    return JsonResponse({'reply': bot_msg})

@login_required
def add_to_cart(request, item_id):
    cart = request.session.get('cart', {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + 1
    request.session['cart'] = cart
    return redirect('menu')

@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    if request.method == 'POST':
        for key in request.POST:
            if key.startswith('qty_'):
                item_id = key.split('_')[1]
                qty = int(request.POST[key])
                if qty > 0:
                    cart[item_id] = qty
                else:
                    cart.pop(item_id, None)
        request.session['cart'] = cart
        return redirect('cart')

    items = []
    total = 0
    for item_id, qty in cart.items():
        item = get_object_or_404(MenuItem, id=item_id)
        items.append({'item': item, 'qty': qty, 'subtotal': item.price * qty})
        total += item.price * qty
    return render(request, 'cart.html', {'cart_items': items, 'total': total})

@login_required
def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('menu')

    order = Order.objects.create(user=request.user)
    for item_id, qty in cart.items():
        item = get_object_or_404(MenuItem, id=item_id)
        OrderItem.objects.create(order=order, menu_item=item, quantity=qty)

    send_mail(
        'Order Confirmation - Your Fast Food Order',
        f'Hello {request.user.username},\n\nYour order (Order ID: #{order.id}) has been successfully placed!',
        settings.EMAIL_HOST_USER,
        [request.user.email],
        fail_silently=False,
    )

    request.session['cart'] = {}
    return render(request, 'order_success.html', {'order': order})

# @login_required
# def order_history(request):
#     orders = Order.objects.filter(user=request.user).order_by('-created_at')
#     return render(request, 'order_history.html', {'orders': orders})

@login_required
def order_history(request):
    # orders = Order.objects.filter(user=request.user)
    orders = Order.objects.select_related('user').prefetch_related('items__menu_item').filter(user=request.user)
    return render(request, 'order_history.html', {'orders': orders})


class CustomLogoutView(LogoutView):
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


from django.shortcuts import render, redirect
from .models import Profile
from .forms import ProfileForm

@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {'form': form})


import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def create_payment_intent(request):
    if request.method == "POST":
        # Create payment intent with cart total
        total = 1000  # Total amount in cents (₹10 for this example)
        intent = stripe.PaymentIntent.create(
            amount=total,
            currency="inr",
            metadata={'integration_check': 'accept_a_payment'},
        )
        return render(request, 'checkout.html', {'client_secret': intent.client_secret})
