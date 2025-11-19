from django.urls import path
from . import views
from .views import simple_form, add_task, task_list, BookListCreateAPIView, BookDetailAPIView, LoginView, RegisterView, \
    LogoutView, RefreshTokenView, ItemAPIView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.hello, name='hello'),
    path('hello3/', simple_form, name='simple_form'),
    path('add-task/', add_task, name='add_task'),
    path('tasks/', task_list, name='task_list'),
    path('books/', BookListCreateAPIView.as_view()),
    path('books/<int:pk>/', BookDetailAPIView.as_view()),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('items/', ItemAPIView.as_view(), name='item-list'),
    path('items/<int:pk>/', ItemAPIView.as_view(), name='item-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)