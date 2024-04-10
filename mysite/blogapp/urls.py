from django.urls import path
from .views import ArticlesListView, ArticleDetailView, LatestArticlesFeed

app_name = 'blogapp'

urlpatterns = [
    path('list/', ArticlesListView.as_view(), name='article_list'),
    path('detail/<int:pk>/', ArticleDetailView.as_view(), name='article_details'),
    path('latest/feed/', LatestArticlesFeed(), name='article_feed'),
]
