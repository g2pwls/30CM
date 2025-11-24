from django.shortcuts import render
from django.shortcuts import redirect, reverse
from django.views.generic import TemplateView
from shop import models as shop_models
from . import models
def toggle_product(request, product_pk):
    action = request.GET.get("action", None) # 👈 action값 추출
    product = shop_models.Product.objects.get_or_none(pk=product_pk) # 👈 Room Object 가져오기
    if product is not None and action is not None:
        the_list, _ = models.List.objects.get_or_create(
            user=request.user, name="My Favourites Houses"
        ) # 👈 List Object 생성
        if action == "add": # 👈 추가
            the_list.room.add(product)
        elif action == "remove": # 👈 제거
            the_list.room.remove(product)
    return redirect(reverse("shop:detail", kwargs={"pk": product_pk}))
class SeeFavsView(TemplateView): # 👈 즐겨찾기 목록을 TemplateView를 상속하여 보여줍니다.
    template_name = "lists/list_detail.html"
# Create your views here.
