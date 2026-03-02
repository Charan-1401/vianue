from django.urls import path
from .views import CreatePaymentIntentView, WebhookView

urlpatterns = [
    path('intent/<int:order_id>/', CreatePaymentIntentView.as_view(), name='create-intent'),
    path('webhook/', WebhookView.as_view(), name='payments-webhook'),
]
