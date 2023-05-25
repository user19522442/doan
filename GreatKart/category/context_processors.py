from .models import Category
"""
đưa ra toàn bộ sản phẩm 
"""
def menu_links(request):
    links = Category.objects.all()
    return dict(links = links)