from django.contrib.gis.feeds import Feed
from django.shortcuts import render
from django.urls import reverse_lazy, reverse

from django.views.generic import ListView, DetailView

from .models import Article


class ArticlesListView(ListView):
    context_object_name = 'articles'
    queryset = (
        Article.objects
        .select_related("author", "category")
        .prefetch_related("tags")
        .defer("content")
    )


class ArticleDetailView(DetailView):
    template_name = 'blogapp/article_details.html'
    queryset = (
        Article.objects
        .select_related("author", "category")
        .prefetch_related("tags")
    )


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes in blog articles."
    link = reverse_lazy('blogapp:article_list')

    def items(self):
        return (
            Article.objects
            .filter(pub_date__isnull=False)
            .order_by('-pub_date')[:5]
        )

    def item_title(self, item: Article) -> str:
        return item.title

    def item_description(self, item: Article) -> str:
        return item.content[:150]


