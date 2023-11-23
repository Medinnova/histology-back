from django.contrib import admin
from django.urls import path, re_path, include

from django.views.static import serve
from catalog.views import SectionViewSet, CreateSectionView, GetSectionsAPIView
from users.views import *
from gist.views import GistViewSet
from university.views import ConnectUniversity, UniversityViewSet, GenerateCodes
from subscription.views import BuySubscrition, RenewSubscrition
from subscription.views import SubscriptionViewSet
from favourites.views import FavouriteViewSet

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView
)

from rest_framework import routers

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Gist API",
      default_version='v1',
      description="Gist API",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = routers.SimpleRouter()
router.register(r'sections', SectionViewSet)
router.register(r'users', UserViewSet)
router.register(r'universities', UniversityViewSet)
router.register(r'gists', GistViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'favourites', FavouriteViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('docs',  schema_view.with_ui( cache_timeout=0)),#'redoc',
    path('docs1',  schema_view.without_ui( cache_timeout=0)),#'redoc',
    
    re_path('api/', include(router.urls)),
    path('api/user/gists', UserGists.as_view()),

    path('api/auth', UsersAPIView.as_view()),
    path('api/user/exists', UserExistsAPIView.as_view()),
    path('api/user/get', UserGetAPIView.as_view()),
    path('api/register', RegisterAPIView.as_view()),
    
    path('api/sections/create', CreateSectionView.as_view()),
    path('api/sections/for_user', GetSectionsAPIView.as_view()),

    path('api/gists/create', UploadImageView.as_view()),
    
    path('api/favourites', FavouriteView.as_view()),

    path('api/send_confirm_code', SendConfirmationCodeAPIView.as_view()),
    path('api/send_restore_link', SendRestoreLinkAPIView.as_view()),
    path('api/set_password', RestorePasswordAPIView.as_view()),
    
    path('api/universities/connect', ConnectUniversity.as_view()),
    path('api/universities/generate_codes', GenerateCodes.as_view()),

    path('api/subscriptions/buy', BuySubscrition.as_view()),
    path('api/subscriptions/renew', RenewSubscrition.as_view()),

    # Json Web Token URL's 
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify', TokenVerifyView.as_view(), name='token_verify'),

    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
]
