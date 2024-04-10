from typing import Sequence

from django.core.management import BaseCommand
from django.db import transaction

from blogapp.models import Article, Author, Tag, Category


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Creates article")
        author = Author.objects.get(name='igor')
        category = Category.objects.get(name='ddf')
        tags: Sequence[Tag] = Tag.objects.all()
        article, created = Article.objects.get_or_create(
            title="my info job",
            content="my info job adaiohsf dsgjdfgjfdkl.sdgfdd kopdgdgf",
            author=author,
            category=category,
        )
        for tag in tags:
            article.tags.add(tag)
        article.save()
        self.stdout.write(f"Created order {article}")
