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
                     Order)
from .serializers import (UserSerializer,
                          BannerSerializer,
                          CatalogueSerializer,
                          CatalogueWithImageSerializer,
                          MenuSerializer,
                          MenuWithoutIdSerializer,
                          ProductItemSerializer,
                          ProductSerializer,
                          OrderSerializer)


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
    

class CatalogueInHeaderViewSet(viewsets.ViewSet):

    permission_classes = [AllowAny]

    def list(self, request):

        catalogue_objects = Category.objects.all().order_by('queue')

        catalogue_data = CatalogueSerializer(catalogue_objects, many=True).data

        return Response({
            'catalogue': catalogue_data
        })


class HomeViewSet(viewsets.ViewSet):

    permission_classes = [AllowAny]

    def list(self, request):

        banner_objects = Banner.objects.all().order_by('queue')
        menu_objects = Category.objects.all().order_by('queue')
        best_objects = Product.objects.filter(is_best = True, is_active = True)
        discout_objects = Product.objects.filter(discount__gt = 0, is_best = False, is_active = True).order_by('-discount')

        banner_data = BannerSerializer(banner_objects, many=True).data
        menu_data = MenuSerializer(menu_objects, many=True).data
        best_data = ProductItemSerializer(best_objects, many=True).data
        discount_data = ProductItemSerializer(discout_objects, many=True).data

        return Response({
            'banners': banner_data,
            'bests': best_data,
            'discounts': discount_data,
            'menu': menu_data
        })


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

    def list(self, request):

        product_objects = Product.objects.filter(is_active = True)

        product_data = ProductItemSerializer(product_objects, many=True).data

        return Response({'products': product_data,})

    @action(methods=['get'], detail=True)
    def product(self, request, pk=None):
        product_objects = Product.objects.get(pk=pk)
        product_data = ProductSerializer(product_objects).data

        return Response({
            'product': product_data
        })
    

class OrderViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]
    
    def list(self, request):

        orders_objects = Order.objects.filter(user=request.user)

        orders_data = OrderSerializer(orders_objects, many=True).data

        return Response({'orders': orders_data})
    
    @action(methods=['get', 'delete', 'patch', 'post'], detail=True)
    def order(self, request, pk=None):
        
        if request.method in ['GET', 'DELETE', 'PATCH']:
            
            try:
                order_object = Order.objects.get(pk=pk, user=request.user)
            except Order.DoesNotExist:
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if request.method == 'GET':
                order_data = OrderSerializer(order_object).data
                return Response({'order': order_data})
            
            if request.method == 'DELETE':
                order_object.delete()
                return Response({'message': 'Order deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
            
            if request.method == 'PATCH':
                order_data = OrderSerializer(order_object, data=request.data, partial=True)
                if order_data.is_valid():
                    order_data.save()
                    return Response({'order': order_data.data})
                
        elif request.method == 'POST':

            serializer = OrderSerializer(data=request.data)

            if serializer.is_valid():

                serializer.save(user=request.user)

                return Response({'order': serializer.data}, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
