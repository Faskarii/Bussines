from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def cart_view(request):
    return render(request, 'cart/cart.html', {
        'cart_count': request.session.get('cart_count', 0)
    })
