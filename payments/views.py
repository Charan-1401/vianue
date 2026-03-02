from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Payment
from orders.models import Order


class CreatePaymentIntentView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, customer=request.user)
        payment = Payment.objects.create(order=order, amount=order.totals_snapshot.get('total') or 0, currency=order.currency)
        return Response({'payment_id': payment.id, 'client_secret': 'stub_client_secret'})


class WebhookView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        payment = get_object_or_404(Payment, pk=data.get('payment_id'))
        if data.get('status') == 'succeeded':
            payment.status = 'SUCCEEDED'
            payment.save()
            order = payment.order
            order.status = 'CONFIRMED'
            order.save()
            return Response({'ok': True})
        else:
            payment.status = 'FAILED'
            payment.save()
            return Response({'ok': False}, status=status.HTTP_400_BAD_REQUEST)
