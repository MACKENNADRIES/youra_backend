from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status, permissions
from django.http import Http404
from .models import RAKPost, ClaimedRAK, ClaimAction
from .serializers import RAKPostSerializer, ClaimedRAKSerializer, ClaimActionSerializer
from .permissions import IsOwnerOrReadOnly

# View for listing and creating RAKPost instances
class RAKPostList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        rak_posts = RAKPost.objects.all()
        serializer = RAKPostSerializer(rak_posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RAKPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)  # Set owner to the authenticated user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View for retrieving, updating, or deleting a specific RAKPost instance
class RAKPostDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            rak_post = RAKPost.objects.get(pk=pk)
            self.check_object_permissions(self.request, rak_post)  # Check custom permissions
            return rak_post
        except RAKPost.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        rak_post = self.get_object(pk)
        serializer = RAKPostSerializer(rak_post)
        return Response(serializer.data)

    def put(self, request, pk):
        rak_post = self.get_object(pk)
        serializer = RAKPostSerializer(
            instance=rak_post,
            data=request.data,
            partial=True  # Allow partial updates
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        rak_post = self.get_object(pk)
        rak_post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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


class PayItForwardView(APIView):
    def post(self, request, pk):
        original_rak = RAKPost.objects.get(pk=pk)
        if original_rak.is_completed:
            new_rak = RAKPost(
                user=request.user,
                description=request.data.get('description'),
                is_paid_forward=True
            )
            new_rak.save()
            original_rak.pay_it_forward()  # Mark original RAK as paid forward
            return Response({'status': 'Pay It Forward created successfully'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Original RAK is not completed'}, status=status.HTTP_400_BAD_REQUEST)
    
class ClaimList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        claims = ClaimedRAK.objects.all()
        serializer = ClaimedRAKSerializer(claims, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        # Validate and save the new claim
        serializer = ClaimedRAKSerializer(data=request.data)
        if serializer.is_valid():
            # Automatically set the claimant to the logged-in user
            serializer.save(claimant=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)