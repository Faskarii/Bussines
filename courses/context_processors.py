def cart_count(request):
    cart = request.session.get('cart', {})
    return {
        'cart_count': len(cart)
    }

from .models import Category

def categories_list(request):
    return {
        'categories': Category.objects.all()
    } 