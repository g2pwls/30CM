from django.urls import path
from . import views

app_name = "qna"

urlpatterns = [
    # 1. GET / articles/ 
    path('', views.index, name ='index'), # 게시글 목록
    # 2. GET / articles / new / 
    path('new/', views.new, name ='new'), # 게시글 작성 양식 (GET)
    # 3. POST / articles / new / 
    path('<int:pk>/detail/', views.detail, name='qna:detail'),
    # path('create/', views.create, name ='create'), # 게시글 생성! (POST)
    path('<int:pk>/delete/', views.delete, name='qna:delete'),
    # 4. GET / articles / 1/ 
    path('<int:pk>/', views.detail, name= 'detail'),
    # 5. POST / articles /1/ delete/ 
    path('<int:pk>/delete/', views.delete, name='delete'),
    # 6. GET /articles /1/edit/
    path('<int:pk>/edit/', views.edit,name ='edit'), # 게시글 수정 양식 (GET)
    # 7. POST / articles/1/edit/
    # path('update/<int:pk>/', views.update, name = 'update'), # 게시글 수정! (POST)
    path('category/<slug:slug>/', views.index, name='category_qna'),

    path('<int:pk>/reply/', views.reply, name='qna:reply'),
    path('<int:pk>/reply/edit/', views.reply_edit, name='qna:reply_edit'),
    path('<int:pk>/reply/delete/', views.reply_delete, name='qna:reply_delete'),
]