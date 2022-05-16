from .models import Category

#creating context manager for categories to show in layout.html
def categories(request):
    categories = Category.objects.all()
    return {"categories":[str(category) for category in categories]}