from django.shortcuts import render

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from base.models import Product, Order, OrderItem, ShippingAddress
from base.serializers import ProductSerializer, OrderSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from datetime import datetime


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user
    data = request.data
    orderItems = data['orderItems']

    if orderItems and len(orderItems) == 0:
        return Response({'detail': 'No Order Items'}, status=status.HTTP_400_BAD_REQUEST)
    else:

        # 1 create order

        order = Order.objects.create(
            user=user,
            paymentMethod=data['paymentMethod'],
            taxPrice= data['taxPrice'],
            shippingPrice= data['shippingPrice'],
            totalPrice=data['totalPrice'],


        )

        # 2 create shipping address

        shipping = ShippingAddress.objects.create(
            order=order,
            address=data['shippingAddress']['address'],
            city=data['shippingAddress']['city'],
            postalCode=data['shippingAddress']['Postalcode'],
            country=data['shippingAddress']['country'],

        )
        # 3 create order items add set order to oritem relationship
        for i in orderItems:
            product = Product.objects.get(_id=i['product'])

            item = OrderItem.objects.create(
                product= product,
                order=order,
                name=product.name,
                qty=i['qty'],
                price=i['price'],
                image=product.image.url,

            )
        # 4 update the stock

            product.countInStock -= item.qty
            product.save()
        Serializer = OrderSerializer(order, many=False)
        return Response(Serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrder(request):
    user = request.user
    orders = user.order_set.all()
    Serializer = OrderSerializer(orders, many=True)
    return Response(Serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrders(request):
    orders = Order.objects.all()
    Serializer = OrderSerializer(orders, many=True)
    return Response(Serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request,pk):
    
    user = request.user

   
    try:
        order= Order.objects.get(_id=pk)
        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)
        else:
            Response({'detail':'Not authorized to view this order'}, status=status.HTTP_400_BAD_REQUEST)
    
    except:
        return Response({'detail','Order does not exists'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    order = Order.objects.get(_id=pk)

    order.isPaid = True
    order.paidAt= datetime.now()
    order.save()
    return Response('Order was Paid')


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrdertodeliver(request, pk):
    order = Order.objects.get(_id=pk)

    order.isDelivered = True
    order.deliveredAt= datetime.now()
    order.save()
    return Response('Order was delivered')
