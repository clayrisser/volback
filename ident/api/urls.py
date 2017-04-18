from django.conf.urls import url, include
from rest_framework import routers
from api.views import test_view
from api.views import user_view

router = routers.DefaultRouter()
router.register(r'users', user_view.UserViewSet)
router.register(r'groups', user_view.GroupViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^test', test_view.TestView.as_view())
]
