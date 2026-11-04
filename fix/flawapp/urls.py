from django.urls import path
from . import views

urlpatterns = [
    path('', views.indexView, name='index'),
    path('register/', views.registerView, name='register'),
    path('login/', views.loginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('add/', views.addView, name='add'),
    path('release/', views.releaseView, name='release'),
    path('search/', views.searchView, name='search'),
    path('listall/', views.listallView, name='listall'),
    path('delete/', views.deleteView, name='delete'),
]
