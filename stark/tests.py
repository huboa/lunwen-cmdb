from django.test import TestCase

# Create your tests here.

from rbac import models
admin_obj = models.UserInfo.objects.filter(id=1)