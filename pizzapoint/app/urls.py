from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib.auth import views as auth_views

from .views import (CatalogueInHeaderViewSet,
                    BannerViewSet,
                    NewProductVuewSet,
                    DiscountProductVuewSet,
                    MenuViewSet,
                    UserViewSet,
                    CatalogueViewSet,
                    ProductsViewSet,
                    OrderItemViewSet,
                    OrderViewSet,
                    ActiveOrderViewSet,
                    CompletedOrderViewSet)


router = routers.DefaultRouter()
router.register(r'catalogue_in_header', CatalogueInHeaderViewSet, basename='catalogue_in_header')
router.register(r'banner', BannerViewSet, basename='banner')
router.register(r'new_product', NewProductVuewSet, basename='new_product')
router.register(r'discount_product', DiscountProductVuewSet, basename='discount_product')
router.register(r'menu', MenuViewSet, basename='menu')
router.register(r'user', UserViewSet, basename='user')
router.register(r'catalogue', CatalogueViewSet, basename='catalogue')
router.register(r'products', ProductsViewSet, basename='products')
router.register(r'order_items', OrderItemViewSet, basename='order_items')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'active_orders', ActiveOrderViewSet, basename='active_orders')
router.register(r'completed_orders', CompletedOrderViewSet, basename='completed_orders')

urlpatterns = [

    path('api/', include(router.urls)),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    
]
