import json
from urllib import request
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import HttpResponse, redirect
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import requests

from cart.models import CartItem
from .models import ColorCategory, Like, Payment, Product, Category, NestedSubCategory, SizeCategory, SubCategory

from users.models import User
from . import models, forms
from .forms import SearchForm
from shop import models as shop_models
from django.views.generic import ListView, DetailView
from django.http import Http404
from django.shortcuts import get_object_or_404

from django.shortcuts import render, get_object_or_404
from .models import Product
from qna.models import Qna, QnaCategory
from shop.models import Category
from django.db.models import Count, Q
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

def shopping_info(request):
    payments = Payment.objects.filter(user=request.user).prefetch_related('items__product')

    return render(request, 'users/shopping_info.html', {'payments': payments})

@csrf_exempt
def payment_complete(request):
    if request.method == 'POST':
        try:
            print("Request Headers:", request.headers)
            print("Raw Body:", request.body)

            # JSON 요청 본문 파싱
            data = json.loads(request.body)
            imp_uid = data.get('imp_uid', 'unknown_uid')
            merchant_uid = data.get('merchant_uid', 'unknown_merchant')
            paid_amount = data.get('paid_amount', 0)
            status = data.get('status', 'unknown_status')

            print("Parsed Data:", data)

            # 주문 데이터 확인 또는 생성
            order, created = Payment.objects.get_or_create(
                merchant_uid=merchant_uid,
                defaults={
                    'user': request.user if request.user.is_authenticated else None,
                    'amount': paid_amount,
                    'status': "ready",
                }
            )

            # 중복된 imp_uid 확인
            if not created and order.imp_uid == imp_uid:
                return JsonResponse({'status': 'error', 'message': 'Duplicate payment detected'}, status=400)

            # 아임포트 액세스 토큰 발급
            token_payload = {
                "imp_key": "7858823464676216",
                "imp_secret": "Uv8R4MCeHQv0GINLD9yVxm8v2pmNffuwu8mjPfi3mkYYrk9bFMF69U2cQzYibCiWK8XVag55H24ghMKB"
            }
            response = requests.post('https://api.iamport.kr/users/getToken', data=token_payload)
            token_data = response.json()

            if not token_data.get('response'):
                print("Token Error:", token_data)
                return JsonResponse({'error': 'Failed to get access token'}, status=400)

            access_token = token_data['response']['access_token']
            print("Access Token:", access_token)

            # 결제 정보 조회
            headers = {"Authorization": access_token}
            response = requests.get(f'https://api.iamport.kr/payments/{imp_uid}', headers=headers)
            payment_data = response.json()

            if not payment_data.get('response'):
                print("Payment Data Error:", payment_data)
                return JsonResponse({'error': 'Failed to get payment information'}, status=400)

            # 결제 금액 및 상태 검증
            amount_paid = payment_data['response']['amount']
            payment_status = payment_data['response']['status']
            expected_amount = order.amount

            if expected_amount != amount_paid:
                print("Payment Amount Mismatch")
                return JsonResponse({'status': "forgery", 'message': "위조된 결제 시도"}, status=400)

            # 결제 상태 처리
            order.imp_uid = imp_uid
            order.status = payment_status
            order.is_paid = (payment_status == 'paid')
            order.save()

            if payment_status == 'ready':  # 가상계좌 발급
                return JsonResponse({'status': "vbankIssued", 'message': "가상계좌 발급 성공"})
            elif payment_status == 'paid':  # 결제 성공
                return JsonResponse({'status': "success", 'message': "일반 결제 성공"})

            print("Unexpected Payment Status:", payment_status)
            return JsonResponse({'status': "error", 'message': "결제 상태 오류"}, status=400)

        except json.JSONDecodeError:
            print("JSON Decode Error")
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            print("Unexpected Error:", e)
            return JsonResponse({'error': str(e)}, status=500)
    else:
        print("Invalid Request Method")
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

def checkout_selected(request):
    if request.method == "POST":
        selected_item_ids = request.POST.getlist("selected_items")
        if not selected_item_ids:  # 선택된 항목이 없을 경우
            return render(request,"shop/checkout.html") # 장바구니 페이지로 리다이렉트
        selected_items = CartItem.objects.filter(id__in=selected_item_ids)

        session_selected_items = []
        for item in selected_items:
            session_selected_items.append({
                "product_id": item.product.id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "size_id": item.size.id if item.size else None,
                "size_name": item.size.name if item.size else None,
                "color_id": item.color.id if item.color else None,
                "color_name": item.color.name if item.color else None,
                "price": item.product.price,
            })

        request.session["selected_items"] = session_selected_items
        request.session["direct_purchase"] = False  # 장바구니에서 구매임을 명시
        request.session.modified = True
        print("DEBUG: Session Selected Items:", request.session["selected_items"])  # 세션 데이터 확인

        return redirect("shop:checkout")
    
    # GET 요청일 경우 기본 cart.html로 리디렉션
    print("DEBUG: GET request received, redirecting to cart")

    return render(request,"shop/checkout.html")

def direct_purchase(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        size_id = request.POST.get("sizecategory")
        color_id = request.POST.get("colorcategory")

        size = get_object_or_404(SizeCategory, id=size_id) if size_id else None
        color = get_object_or_404(ColorCategory, id=color_id) if color_id else None

        # 바로 구매 아이템 데이터 생성
        direct_item = {
            "product_name": product.name,
            "quantity": quantity,
            "size_id": size.id if size else None,
            "size_name": size.name if size else None,
            "color_id": color.id if color else None,
            "color_name": color.name if color else None,
            "price": product.price * quantity,
        }

        # 세션에 저장
        request.session["direct_product_items"] = direct_item
        request.session["direct_purchase"] = True
        request.session.modified = True  # 세션 변경 사항 저장

        # checkout 페이지로 리다이렉트
        return redirect("shop:checkout")

    return redirect("cart:cart")

def checkout(request):
    items = []
    total = 0

    if request.session.get("direct_purchase"):
        direct_item = request.session.get("direct_product_items", {})  # 딕셔너리로 가져옴
        if direct_item:  # 데이터가 있을 경우
            items = [  # 리스트 형태로 변환
                {
                    "product_name": direct_item["product_name"],
                    "quantity": direct_item["quantity"],
                    "size_name": direct_item["size_name"],
                    "color_name": direct_item["color_name"],
                    "price": direct_item["price"],
                }
            ]
        total = direct_item["price"] * direct_item["quantity"]
        return render(request, "shop/checkout.html", {
            "direct_items": items,  # 리스트 형태로 템플릿에 전달
            "selected_items": None,
            "total": total,
        })
    # 장바구니 항목 처리
    selected_items = request.session.get("selected_items", [])
    for item in selected_items:
        product = Product.objects.get(id=item["product_id"])
        size = SizeCategory.objects.get(id=item["size_id"]).name if item.get("size_id") else None
        color = ColorCategory.objects.get(id=item["color_id"]).name if item.get("color_id") else None
        items.append({
            "product_name": product.name,
            "quantity": item["quantity"],
            "size_name": size,
            "color_name": color,
            "price": product.price * item["quantity"],
        })
    total = sum(item["price"] for item in items)
    return render(request, "shop/checkout.html", {
        "direct_items": None,
        "selected_items": items,
        "total": total,
    })

@csrf_exempt
@login_required
def toggle_like(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user

    # 좋아요 상태 토글
    if Like.objects.filter(user=user, product=product).exists():
        # 이미 좋아요한 경우, 좋아요 취소
        Like.objects.filter(user=user, product=product).delete()
        liked = False
    else:
        # 좋아요 추가
        Like.objects.create(user=user, product=product)
        liked = True

    # 좋아요 수를 포함하여 JSON 응답 반환
    return JsonResponse({'liked': liked, 'like_count': product.like_count()})

def search(request):
    # GET 요청으로부터 검색 파라미터 수집
    name = request.GET.get("name", "")
    category = int(request.GET.get("category", 0))
    color_id = int(request.GET.get("ColorCategory", 0))
    price = int(request.GET.get("price", 0))
    s_hosts = request.GET.getlist("hosts", [])

    # 필터 조건
    filter_args = {}

    if name:
        filter_args["name__icontains"] = name  # 대소문자 구분 없이 이름 검색

    if category != 0:
        filter_args["category__pk"] = category  # 카테고리 필터링

    if color_id != 0:
        filter_args["color__pk"] = color_id  # 색상 필터링

    if price != 0:
        filter_args["price__lte"] = price  # 가격 필터링

    if s_hosts:
        filter_args["host__id__in"] = s_hosts  # 호스트 필터링

    # 필터링된 상품 검색
    products = Product.objects.filter(**filter_args)

    # 페이징 처리 추가
    page = request.GET.get("page", 1)
    paginator = Paginator(products, 10)  # 한 페이지에 10개씩 표시

    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    # 카테고리와 호스트 선택지
    categories = models.Category.objects.all()
    color_categories = models.ColorCategory.objects.all()
    hosts = User.objects.all()

    # 템플릿에 넘길 컨텍스트
    context = {
        "name": name,
        "s_category": category,
        "s_ColorCategories": [color_id],
        "price": price,
        "s_hosts": s_hosts,
        "categories": categories,
        "ColorCategories": color_categories,
        "hosts": hosts,
        "products": products_page,  # 페이징된 상품 목록
        "page_obj": products_page,  # 페이지 정보 객체
    }

    return render(request, "shop/search.html", context)

def all_products(request):
    page = request.GET.get("page", 1)
    products = Product.objects.all().order_by('name')
    paginator = Paginator(products, 10)
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger: 
        products_page = paginator.page(1)
    except EmptyPage: 
        products_page = paginator.page(paginator.num_pages)

    context = {
        "products": products_page,  # 현재 페이지에 해당하는 제품 리스트
        "page_obj": products_page,  # 페이지 정보 객체 (템플릿에서 사용 가능)
    }
    return render(request, 'shop/product_list.html', context)

class ProductDetail(DetailView):
    model = models.Product
    template_name = "shop/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.request.GET.get('category_id')
        if category_id:
            context['qnas'] = Qna.objects.filter(product=self.object, category_id=category_id)  # 선택된 카테고리의 Q&A만 필터링
            context['selected_category_id'] = int(category_id)  # 선택된 카테고리 ID 저장
        else:
            context['qnas'] = Qna.objects.filter(product=self.object)  # 모든 Q&A 가져옴
            context['selected_category_id'] = None
        context['qna_categories'] = QnaCategory.objects.annotate(
            qna_count=Coalesce(Count('qna', filter=Q(qna__product=self.object)), 0)).order_by('id')
        context['total_qna_count'] = context['qnas'].count()

        context['sizes'] = SizeCategory.objects.all()
        context['colors'] = ColorCategory.objects.all()

        user = self.request.user
        product = self.object  # 현재 조회 중인 Product 객체
       

        if user.is_authenticated:
            # 사용자와 제품 간의 좋아요 여부를 확인하고 변수에 저장
            context['user_has_liked'] = Like.objects.filter(user=user, product=product).exists()
        else:
            context['user_has_liked'] = False  # 로그인하지 않은 경우 기본적으로 False

        return context
    


class ProductListByCategory(ListView):
    model = models.Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(category__slug=self.kwargs['slug'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

class ProductListBySubCategory(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
            category__slug=self.kwargs['category_slug'],
            subcategory__slug=self.kwargs['subcategory_slug']
            return Product.objects.filter(
                category__slug=category__slug,
                subcategory__slug=subcategory__slug
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subcategory = get_object_or_404(SubCategory, slug=self.kwargs['subcategory_slug'])
        context['nested_subcategories'] = subcategory.nested_subcategories.all()
        return context

class ProductListByNestedSubCategory(ListView):
    model = Product
    template_name = "shop/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        subcategory_slug = self.kwargs['subcategory_slug']
        nested_subcategory_slug = self.kwargs['nested_subcategory_slug']
        
        return Product.objects.filter(
            category__slug=category_slug,
            subcategory__slug=subcategory_slug,
            nested_subcategory__slug=nested_subcategory_slug
        ).select_related('category', 'subcategory', 'nested_subcategory')
    

class HomeView(ListView):
    """HomeView Definition"""
    model = models.Product
    paginate_by = 10  # 👈 한 페이지에 제한할 Object 수
    paginate_orphans = 5  # 👈 짜투리 처리
    page_kwarg = "page" # 👈 페이징할 argument
    context_object_name = "products"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # 좋아요 상태 확인 및 추가
        if user.is_authenticated:
            liked_product_ids = Like.objects.filter(user=user).values_list('product_id', flat=True)
            for product in context['products']:
                product.user_has_liked = product.id in liked_product_ids
        else:
            for product in context['products']:
                product.user_has_liked = False

        context['is_home'] = True
        return context


from django.shortcuts import render
from .models import Product, Like

def product_list(request):
    products = Product.objects.all()

    # 각 상품에 대해 현재 사용자가 좋아요를 눌렀는지 확인
    for product in products:
        product.user_has_liked = product.likes.filter(user=request.user).exists()

    return render(request, 'shop/product_list.html', {
        'products': products,
    })
