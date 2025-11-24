from .models import Category, NestedSubCategory


def categories_processor(request):
    return {
        'categories': Category.objects.all()
    }
