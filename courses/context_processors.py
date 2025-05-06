def cart_count(request):
    cart = request.session.get('cart', {})
    return {
        'cart_count': len(cart)
    }

from .models import Category

def categories(request):
    # Get only parent categories (those without a parent)
    parent_categories = Category.objects.filter(parent=None).prefetch_related('children')
    
    # Create a dictionary of categories with their children
    categories_dict = {
        'parent_categories': parent_categories,
    }
    
    return categories_dict 