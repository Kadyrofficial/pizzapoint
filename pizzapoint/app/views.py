from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated,
                                        AllowAny)

from .utils import (send_verification_code,
                    verify_code)
from .models import (User,
                     Banner,
                     Category,
                     Product,
                     OrderItem,
                     Order)
from .serializers import (UserSerializer,
                          BannerSerializer,
                          CatalogueSerializer,
                          CatalogueWithImageSerializer,
                          MenuSerializer,
                          MenuWithoutIdSerializer,
                          ProductItemSerializer,
                          ProductSerializer,
                          OrderItemSerializer,
                          CreateOrderItemSerializer,
                          OrderSerializer,
                          CreateOrderSerializer,
                          OrderStatusSerializer)


class CatalogueInHeaderViewSet(viewsets.ViewSet):

    permission_classes = [AllowAny]

    def list(self, request):

        catalogue_objects = Category.objects.all().order_by('queue')
        catalogue_data = CatalogueSerializer(catalogue_objects, many=True).data

        return Response({
            'catalogue': catalogue_data
        })


class BannerViewSet(viewsets.ViewSet):

    permission_classes = [AllowAny]

    def list(self, request):

        banner_objects = Banner.objects.all().order_by('queue')
        banner_data = BannerSerializer(banner_objects, many=True).data

        return Response({
            'banners': banner_data,
        })


class NewProductVuewSet(viewsets.ViewSet):

    permission_classes = [AllowAny]

    def list(self, request):
    
        best_objects = Product.objects.filter(is_best = True, is_active = True)
        best_data = ProductItemSerializer(best_objects, many=True).data

        return Response({
            'news': best_data,
        })


class DiscountProductVuewSet(viewsets.ViewSet):

    permission_classes = [AllowAny]

    def list(self, request):
    
        discout_objects = Product.objects.filter(discount__gt = 0, is_best = False, is_active = True).order_by('-discount')
        discount_data = ProductItemSerializer(discout_objects, many=True).data

        return Response({
            'discounts': discount_data,
        })


class MenuViewSet(viewsets.ViewSet):

    permission_classes = [AllowAny]

    def list(self, request):

        menu_objects = Category.objects.all().order_by('queue')
        menu_data = MenuSerializer(menu_objects, many=True).data
        
        return Response({
            'menu': menu_data
        })


class UserViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self, request):

        user_objects = User.objects.get(id=request.user.id)

        user_data = UserSerializer(user_objects).data

        return Response({'profile': user_data})

    @action(methods=['post'], detail=False)
    def register(self, request):

        phone_number = request.data.get('phone_number')
        username = request.data.get('username')

        if User.objects.filter(phone_number=phone_number).exists():
            return Response({'message': 'User with this phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, phone_number=phone_number)

        send_verification_code(phone_number)

        return Response({'message': 'Verification code sent'}, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=False)
    def verify(self, request):

        phone_number = request.data.get('phone_number')
        code = request.data.get('code')

        user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            return Response({'message': 'Invalid phone number'}, status=status.HTTP_404_NOT_FOUND)

        if verify_code(phone_number, code):

            user.is_phone_verified = True
            user.save()

            token, created = Token.objects.get_or_create(user=user)

            return Response({'message': 'Phone number verified', 'token': token.key})

        return Response({'message': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)
    

class CatalogueViewSet(viewsets.ViewSet):

    permission_classes = [AllowAny]

    def list(self, request):

        category_detail_objects = Category.objects.all().order_by('queue')

        category_detal_data = CatalogueWithImageSerializer(category_detail_objects, many=True).data

        return Response({'catalogue_detail': category_detal_data})

    @action(methods=['get'], detail=True)
    def menu(self, request, pk=None):

        menu_objects = Category.objects.get(pk=pk)

        menu_data = MenuWithoutIdSerializer(menu_objects).data

        return Response({'products of menu': menu_data})


class ProductsViewSet(viewsets.ViewSet):

    permission_classes = [AllowAny]

    @action(methods=['get'], detail=True)
    def product(self, request, pk=None):
        product_objects = Product.objects.get(pk=pk)
        product_data = ProductSerializer(product_objects).data

        return Response({
            'product': product_data
        })
    

class OrderItemViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]
    
    def list(self, request):

        order_items_objects = OrderItem.objects.filter(user=request.user, status__in=[OrderItem.Status.PENDING])

        orders_items_data = OrderItemSerializer(order_items_objects, many=True).data

        return Response({'order_items': orders_items_data})
    
    def create(self, request):

        serializer = CreateOrderItemSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save(user=request.user)

            return Response({'order_item': serializer.data}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get', 'delete', 'patch'], detail=True)
    def order_item(self, request, pk=None):

        try:
            order_item_object = OrderItem.objects.get(pk=pk, user=request.user)
        except OrderItem.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
            
        if request.method == 'GET':
            order_item_data = OrderItemSerializer(order_item_object).data
            return Response({'order_item': order_item_data})
            
        if request.method == 'DELETE':
            order_item_object.delete()
            return Response({'message': 'Order item deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            
        if request.method == 'PATCH':
            order_item_data = OrderItemSerializer(order_item_object, data=request.data, partial=True)
            if order_item_data.is_valid():
                order_item_data.save()
                return Response({'order_item': order_item_data.data})


class OrderViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self, request):

        orders_objects = Order.objects.filter(user=request.user, status__in=[Order.Status.ACTIVE, Order.Status.COMPLETED])
        orders_data = OrderSerializer(orders_objects, many=True).data

        return Response({'orders': orders_data})
    
    def create(self, request):

        serializer = CreateOrderSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save(user=request.user)

            return Response({'message': 'Order successfully'}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    


class ActiveOrderViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self, request):

        active_orders_objects = Order.objects.filter(user=request.user, status__in=[Order.Status.ACTIVE])
        active_orders_data = OrderSerializer(active_orders_objects, many=True).data

        return Response({'active_orders': active_orders_data})
    
    @action(methods=['get', 'patch'], detail=True, url_path='order')

    def order(self, request, pk=None):
        active_orders_objects = Order.objects.get(pk=pk, user=request.user, status__in=[Order.Status.ACTIVE])
        
        if request.method == 'GET':

            order_data = OrderSerializer(active_orders_objects).data

            return Response({'order': order_data})
        
        elif request.method == 'PATCH':
                
            serializer = OrderStatusSerializer(active_orders_objects, data=request.data, partial=True)
            order_data = OrderSerializer(active_orders_objects).data
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Status updated successfully', 'order': order_data})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class CompletedOrderViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self, request):

        completed_orders_objects = Order.objects.filter(user=request.user, status__in=[Order.Status.COMPLETED])
        completed_orders_data = OrderSerializer(completed_orders_objects, many=True).data

        return Response({'completed_orders': completed_orders_data})
