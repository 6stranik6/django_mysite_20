from django.contrib.auth.models import User, Group, Permission
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get()
        groups, created = Group.objects.get_or_create(
            name='profile_manager',
        )
        permissions_profile = Permission.objects.get()
        permissions_logentry = Permission.objects.get()

        groups.permissions.add(permissions_profile)

        user.groups.add(groups)

        user.user_permissions.add(permissions_logentry)

        groups.save()
        user.save()
