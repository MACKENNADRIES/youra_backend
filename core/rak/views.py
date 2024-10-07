from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import RAKPost, ClaimedRAK, ClaimAction
from .serializers import RAKPostSerializer, ClaimedRAKSerializer, ClaimActionSerializer

# View for listing and creating RAKPost instances
class RAKPostList(APIView):
    
    def get(self, request):
        rak_posts = RAKPost.objects.all()
        serializer = RAKPostSerializer(rak_posts, many=True)
        return Response(serializer.data)

    # we want to make an post
    def post(self, request):
        serializer = RAKPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View for listing and creating ClaimedRAK instances
class ClaimedRAKList(APIView):

    def get(self, request):
        claimed_raks = ClaimedRAK.objects.all()
        serializer = ClaimedRAKSerializer(claimed_raks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClaimedRAKSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View for listing and creating ClaimAction instances
class ClaimActionList(APIView):

    def get(self, request):
        claim_actions = ClaimAction.objects.all()
        serializer = ClaimActionSerializer(claim_actions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClaimActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
