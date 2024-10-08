from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status, permissions
from django.http import Http404
from .models import RAKPost, ClaimedRAK, ClaimAction
from .serializers import RAKPostSerializer, ClaimActionSerializer, ClaimedRAKListSerializer, ClaimedRAKDetailSerializer
from .permissions import IsOwnerOrReadOnly, IsClaimantOrReadOnly

# View for listing and creating RAKPost instances
class RAKPostList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
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
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        claimed_raks = ClaimedRAK.objects.all()
        serializer = ClaimedRAKListSerializer(claimed_raks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClaimedRAKListSerializer(data=request.data)
        if serializer.is_valid():
            # Save the claim with the current user as the claimant
            claimed_rak = serializer.save(claimant=request.user)
            # Update the RAKPost status to 'claimed'
            claimed_rak.rak.status = 'claimed'
            claimed_rak.rak.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View for retrieving, updating, or deleting a specific ClaimedRAK instance
class ClaimedRAKDetail(APIView):
    permission_classes = [IsClaimantOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(ClaimedRAK, pk=pk)

    def get(self, request, pk):
        claimed_rak = self.get_object(pk)
        serializer = ClaimedRAKDetailSerializer(claimed_rak)
        return Response(serializer.data)

    def put(self, request, pk):
        claimed_rak = self.get_object(pk)
        serializer = ClaimedRAKDetailSerializer(claimed_rak, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
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

# View for handling the Pay It Forward mechanism
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

# View for handling claims on RAKs
class ClaimRAKView(APIView):
    def post(self, request, rak_id):
        try:
            rak = RAKPost.objects.get(id=rak_id)
            # Call the claim_rak method which includes the logic to check if it's still open
            rak.claim_rak(request.user)
            return Response({"message": "RAK claimed successfully."}, status=status.HTTP_200_OK)
        except RAKPost.DoesNotExist:
            return Response({"error": "RAK not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

