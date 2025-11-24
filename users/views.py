from django.shortcuts import get_object_or_404
from shop.models import Product, Category, ColorCategory
# Create your views here.
from django.urls import reverse
from django.views.generic.edit import UpdateView
from django.views.generic import FormView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.views import View
from django.db.models import Q

from .models import User
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout # 👈 authenticate import
from . import forms

def user_profile(request, username):
    user = get_object_or_404(User, username=username)  # 요청된 username의 사용자 찾기
    selected_category = request.GET.get('category')
    selected_subcategory = request.GET.get('subcategory')
    selected_nested_subcategory = request.GET.get('nested_subcategory')
    selected_color = request.GET.get('color')
    price_upper_range  = request.GET.get('PriceUpper', 1000000)
    price_lower_range  = request.GET.get('PriceLower', 0)

    q = Q(host=user) 

    # 기본적으로 사용자가 작성한 모든 제품을 가져옵니다.
    products = Product.objects.filter(host=user)

    # 선택된 카테고리/서브카테고리/하위 카테고리가 있을 때 필터링 적용
    if selected_category:
        q &= Q(category__slug=selected_category)
    if selected_subcategory:
        q &= Q(subcategory__slug=selected_subcategory)
    if selected_nested_subcategory:
        q &= Q(nested_subcategory__slug=selected_nested_subcategory)
    if selected_color:
        q &= Q(color__slug=selected_color)
    
    # 가격 범위 필터링 추가
    q &= Q(price__range = (price_lower_range,price_upper_range))


     # 필터 조건에 맞는 제품 조회
    products = Product.objects.filter(q)

    # 모든 카테고리와 색상 데이터 전달
    categories = Category.objects.all()
    colors = ColorCategory.objects.all()

    context = {
        'user': user,
        'products': products,
        'categories': categories,
        'colors': colors,
        'selected_category': selected_category,
        'selected_subcategory': selected_subcategory,
        'selected_nested_subcategory': selected_nested_subcategory,
        'selected_color': selected_color,
        'price_upper_range': price_upper_range,
        'price_lower_range': price_lower_range,
    }
    return render(request, 'users/user_profile.html', context)

class LoginView(View):
    def get(self, request):
        form = forms.LoginForm()
        context = {"form": form}
        return render(request, "users/login.html", context)
    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            # print(user) # jewon119@kakao.com
            if user is not None:
                login(request, user)  # 👈 login함수에는 request와 인증한 객체를 전달해요:)
                return redirect(reverse("core:home"))
        context = {"form": form} # 👈 로그인이 안되었다면, form에 담긴 오류메시지가 템플릿으로 전달되요:)
        return render(request, "users/login.html", context)
def log_out(request):
    logout(request) # 👈 request만 보내면 logout을 해줘요:)
    return redirect(reverse("core:home"))


class LoginWithEmailView(View):
    def get(self, request):
        form = forms.LoginForm()
        context = {"form": form}
        return render(request, "users/login_with_email.html", context)
    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            # print(user) # jewon119@kakao.com
            if user is not None:
                login(request, user)  # 👈 login함수에는 request와 인증한 객체를 전달해요:)
                return redirect(reverse("core:home"))
        context = {"form": form} # 👈 로그인이 안되었다면, form에 담긴 오류메시지가 템플릿으로 전달되요:)
        return render(request, "users/login_with_email.html", context)
def log_out(request):
    logout(request) # 👈 request만 보내면 logout을 해줘요:)
    return redirect(reverse("core:home"))  # 이메일 로그인 페이지 템플릿

class JoinWithEmailView(View):
    def get(self, request):
        return render(request, "users/join_with_email.html")

class SignUpView(FormView): # 👈 FormView 상속
    template_name = "users/signup.html" # 👈 render할 Template을 지정해줘요:)
    form_class = forms.SignUpForm # 👈 사용될 Form을 지정해줘요:)
    success_url = reverse_lazy("core:home") # 👈 validate가되면 이동합니다.
    def form_valid(self, form): # 👈 form을 전달받아옵니다.
        form.save() # 👈 form의 save() 매서드 실행
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)
        

class MypageView(DetailView):
    template_name = 'users/mypage.html'
    model = User

    def get_object(self, queryset=None):
        return self.request.user
    
class UpdateUserView(UpdateView):
    model = User
    template_name = 'users/update.html'
    fields = ['email', 'name', 'tel', 'birthday','postcode','address','detail_address','extra_address']

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('users:mypage')
    
from django.views.generic import FormView
from .forms import SignUpForm

from django.http import JsonResponse

class JoinWithEmailView(FormView):
    template_name = "users/join_with_email.html"
    form_class = SignUpForm

    def post(self, request, *args, **kwargs):
        form = self.get_form(data=request.POST)
        if form.is_valid():
            # 유효성 검사 성공
            return JsonResponse({"message": "Success"}, status=200)
        else:
            # 유효성 검사 실패
            return JsonResponse({"errors": form.errors}, status=400)
        

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def validate_email(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email", "").strip()
        if email:
            try:
                User.objects.get(email=email)
                return JsonResponse({"valid": False, "error": "동일한 이메일 주소로 가입된 계정이 있습니다. 기존 계정으로 로그인해주세요."})
            except User.DoesNotExist:
                return JsonResponse({"valid": True})
    return JsonResponse({"valid": False, "error": "잘못된 요청입니다."}, status=400)

from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from django.shortcuts import redirect
from .forms import SignupCompleteForm
from .models import User

def signup_complete(request):
    if request.method == "POST":
        form = SignupCompleteForm(request.POST)
        if form.is_valid():
            email = request.session.get("email")
            password = request.session.get("password")
            if not email or not password:
                return redirect('users:join_with_email')  # 세션 데이터 없으면 처음으로 이동

            # 중복 이메일 확인
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,  # username을 email로 설정
                }
            )
            if created:  # 새로 생성된 경우
                user.set_password(password)
                user.name = form.cleaned_data["name"]
                user.tel = form.cleaned_data["tel"]
                user.birthday = form.cleaned_data["birthday"]
                user.save()

            # 사용자 로그인
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # 올바른 경로 문자열 설정
            login(request, user)  # backend를 자동으로 감지하도록 설정

            return redirect("core:home")
    else:
        form = SignupCompleteForm()

    return render(request, "users/signup_complete.html", {"form": form})





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def store_session_data(request):
    if request.method == "POST":
        data = json.loads(request.body)
        if "email" in data:
            request.session["email"] = data["email"]
        if "password" in data:
            request.session["password"] = data["password"]
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)

from django.shortcuts import render

def shopping_info(request):
    # 쇼핑 정보를 가져오는 로직을 추가 (예: 주문 정보)
    orders = []  # 예시 데이터
    return render(request, 'users/shopping_info.html', {'orders': orders})
def product_reviews(request):
    # 사용자의 상품 리뷰를 가져오는 로직을 추가
    reviews = []  # 예시 데이터
    return render(request, 'users/product_reviews.html', {'reviews': reviews})
from django.contrib.auth.decorators import login_required  # login_required 데코레이터 추가
from django.shortcuts import render
from qna.models import Qna

@login_required  # 데코레이터 적용
def product_qna(request):
    # 현재 로그인한 사용자의 QnA 필터링
    qnas = Qna.objects.filter(writer=request.user).select_related('product', 'reply')

    context = {
        'qnas': qnas,
    }
    return render(request, 'users/product_qnalist.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def like_products(request):
    # 현재 사용자가 좋아요한 상품 리스트
    like_products = request.user.like_products.all()
    return render(request, "users/like_products.html", {"like_products": like_products})

