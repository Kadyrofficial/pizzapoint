from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (CatalogueInHeaderViewSet,
                    HomeViewSet,
                    UserViewSet,
                    CatalogueViewSet,
                    ProductsViewSet,
                    OrderViewSet,)


router = routers.DefaultRouter()
router.register(r'catalogue_in_header', CatalogueInHeaderViewSet, basename='catalogue_in_header')
router.register(r'home', HomeViewSet, basename='home')
router.register(r'user', UserViewSet, basename='user')
router.register(r'catalogue', CatalogueViewSet, basename='catalogue')
router.register(r'products', ProductsViewSet, basename='products')
router.register(r'orders', OrderViewSet, basename='orders')


urlpatterns = [

    path('api/', include(router.urls)),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]
