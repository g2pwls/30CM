from datetime import timezone
from django.shortcuts import render, redirect, get_object_or_404

from users.decorators import login_message_required
from .models import Qna, Reply
from qna.models import QnaCategory
from qna import models
from .models import Qna, QnaCategory
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.http import HttpResponse, HttpResponseForbidden
from django.template.loader import render_to_string
from django.db.models.functions import Coalesce
@login_message_required

# Create your views here.
def index(request):
    # Database 조회
    qna_categories = QnaCategory.objects.order_by('id').annotate(qna_count=Coalesce(Count('qna'), 0)).order_by('id')
    category_id = request.GET.get('category_id')
    selected_category_id = int(category_id) if category_id else None
    # 선택된 카테고리에 따른 게시물 필터링
    if category_id:
        qnas = Qna.objects.filter(category_id=category_id)
        selected_category_id = int(category_id)
    else:
        qnas = Qna.objects.all()
        selected_category_id = None

    total_qna_count = qnas.count()

    context = {
        'qnas': qnas,
        'qna_categories': qna_categories,
        'selected_category_id': selected_category_id,
        'total_qna_count': total_qna_count,  # 전체 QnA 수 추가
    }
    return render(request, 'qna_index.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from .models import Qna, QnaCategory, Product
from django.shortcuts import redirect

def new(request): 
    qna_id = int(request.GET.get("QnaCategory", 0))
    filter_args = {}

    if qna_id != 0:
        filter_args["qna__pk"] = qna_id
    # Product 객체 가져오기
    product_id = request.GET.get("product_id")
    if not product_id:
        # product_id가 없을 때, 전체 상품 페이지나 다른 페이지로 리디렉션
        return HttpResponse("product_id가 전달되지 않았습니다.")

    product = get_object_or_404(Product, id=product_id)
    # 나머지 QnA 생성 로직
    if request.method == 'POST': 
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('Qnacategory')
        is_private = request.POST.get('is_private') == 'on'
        category = QnaCategory.objects.get(pk=category_id)

        # QnA 생성 후 저장
        qna = Qna(
            title=title, 
            content=content, 
            writer=request.user, 
            category=category, 
            is_private=is_private, 
            product=product)
        qna.save()
        return redirect('shop:product_detail', pk=product.id)  # 상품 상세 페이지로 리디렉션

    else: 
        qna_categories = QnaCategory.objects.all()
        context = {
            "s_QnaCategories": [qna_id],
            "QnaCategories": qna_categories,
            "product": product,
        }
        return render(request, 'qna_new.html', context)


def detail(request, pk):
    # Database 조회: 단 하나의 data
    qna = Qna.objects.get(pk=pk)
    
    if qna.is_private and not (request.user == qna.writer or request.user.is_staff):
        return HttpResponseForbidden("이 게시물은 비밀글입니다.")

    detail_html = render_to_string('qna_detail.html', {'qna': qna})
    return HttpResponse(detail_html)


def delete(request, pk): # POST
    # Database 삭제 (조회 + 삭제)
    # 1. 조회
    qna = Qna.objects.get(pk=pk)
    # 2. 삭제
    qna.delete()

    return redirect('qna:index')


from django.http import JsonResponse
from django.template.loader import render_to_string

def edit(request, pk):
    qna = Qna.objects.get(pk=pk)
    qna_categories = QnaCategory.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('Qnacategory')
        is_private = request.POST.get('is_private') == 'on'

        qna.title = title
        qna.content = content
        qna.category = QnaCategory.objects.get(pk=category_id)
        qna.is_private = is_private
        qna.save()

        return JsonResponse({"success": True}) 

    # AJAX 요청 시 편집 폼만 반환
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form_html = render_to_string('qna_edit_form.html', {
            'qna': qna,
            'QnaCategories': qna_categories,
            'is_private': qna.is_private,
        })
        return HttpResponse(form_html)

    # 일반 요청
    return render(request, 'qna_edit.html', {
        'qna': qna,
        'QnaCategories': qna_categories,
        'is_private': qna.is_private,
    })


from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse

@staff_member_required
def reply(request, pk):
    qna = Qna.objects.get(pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content')
        # 이미 답변이 없는 경우에만 저장
        if not hasattr(qna, 'reply'):
            qna.reply = Reply(content=content, qna=qna, writer=request.user)
            qna.reply.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "이미 답변이 있습니다."})

    return JsonResponse({"success": False, "error": "잘못된 요청입니다."})

@staff_member_required
def reply_edit(request, pk):
    qna = Qna.objects.get(pk=pk)
    if request.method == 'POST' and hasattr(qna, 'reply'):
        content = request.POST.get('content')
        qna.reply.content = content
        qna.reply.save()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "잘못된 요청입니다."})

# 답변 삭제 뷰
@staff_member_required
def reply_delete(request, pk):
    qna = Qna.objects.get(pk=pk)
    if request.method == 'POST' and hasattr(qna, 'reply'):
        qna.reply.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "잘못된 요청입니다."})