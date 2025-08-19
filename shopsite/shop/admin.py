from django.contrib import admin
from django import forms
from . import models
from .models import Category, Product, SubCategory, NestedSubCategory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # SubCategory가 선택된 경우에만 필터링
        if 'subcategory' in self.data:
            try:
                subcategory_id = int(self.data.get('subcategory'))
                self.fields['nested_subcategory'].queryset = NestedSubCategory.objects.filter(
                    parent_subcategory_id=subcategory_id
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.subcategory:
            self.fields['nested_subcategory'].queryset = NestedSubCategory.objects.filter(
                parent_subcategory=self.instance.subcategory
            )
        else:
            self.fields['nested_subcategory'].queryset = NestedSubCategory.objects.none()


@admin.register(models.ColorCategory)
class ColorCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(models.SizeCategory)
class SizeCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(models.NestedSubCategory)
class NestedSubCategoryAdmin(admin.ModelAdmin):
    pass

class NestedSubCategoryInline(admin.TabularInline):
    model = NestedSubCategory
    extra = 1

@admin.register(models.SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug']
    list_filter = ['category']
    inlines = [NestedSubCategoryInline]


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ['name', 'category', 'subcategory', 'nested_subcategory', 'price', 'stock']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "nested_subcategory":
            # 객체를 수정할 때
            if hasattr(request, "_obj_") and request._obj_ and request._obj_.subcategory:
                kwargs["queryset"] = NestedSubCategory.objects.filter(
                    parent_subcategory=request._obj_.subcategory
                )
            # 새로운 객체를 추가할 때
            elif "subcategory" in request.GET:
                try:
                    subcategory_id = int(request.GET.get("subcategory"))
                    kwargs["queryset"] = NestedSubCategory.objects.filter(
                        parent_subcategory_id=subcategory_id
                    )
                except (ValueError, TypeError):
                    kwargs["queryset"] = NestedSubCategory.objects.none()
            else:
                kwargs["queryset"] = NestedSubCategory.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)
# Register your models here.


