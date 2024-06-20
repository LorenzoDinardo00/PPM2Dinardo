from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'), 
    path('register/', views.register, name='register'),
    path('create-post/', views.create_post, name='create_post'),
    path('', views.StartingPageView.as_view(), name='starting-page'),
    path('posts', views.AllPostsView.as_view(), name='posts-page'),
    path('posts/<slug:slug>', views.SinglePostView.as_view(), name='post-detail-page'),
    path('read-later', views.ReadLaterView.as_view(), name='read-later'),

]
