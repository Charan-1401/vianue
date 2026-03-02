from rest_framework import views, permissions
from rest_framework.response import Response
from venues.models import Venue
from services.models import ServiceListing
from .serializers import SimpleVenueSerializer, SimpleServiceSerializer


class AdminPendingVenuesView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        qs = Venue.objects.filter(status='PENDING')
        serializer = SimpleVenueSerializer(qs, many=True)
        return Response(serializer.data)


class AdminApproveVenueView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        v = Venue.objects.get(pk=pk)
        v.status = 'APPROVED'
        v.save()
        return Response({'status': 'approved'})


class AdminRejectVenueView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        v = Venue.objects.get(pk=pk)
        v.status = 'REJECTED'
        v.save()
        return Response({'status': 'rejected'})


class AdminPendingServicesView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        qs = ServiceListing.objects.filter(status='PENDING')
        serializer = SimpleServiceSerializer(qs, many=True)
        return Response(serializer.data)


class AdminApproveServiceView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        s = ServiceListing.objects.get(pk=pk)
        s.status = 'APPROVED'
        s.save()
        return Response({'status': 'approved'})


class AdminRejectServiceView(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        s = ServiceListing.objects.get(pk=pk)
        s.status = 'REJECTED'
        s.save()
        return Response({'status': 'rejected'})
