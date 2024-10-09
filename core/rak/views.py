from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from django.http import Http404
from datetime import timezone
from .models import RandomActOfKindness, RAKClaim, ClaimAction
from .serializers import RandomActOfKindnessSerializer, RAKClaimSerializer, ClaimActionSerializer, RAKClaimListSerializer
from .permissions import IsOwnerOrReadOnly, IsClaimantOrReadOnly

# View for listing and creating RandomActOfKindness instances
class RandomActOfKindnessList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        rak_posts = RandomActOfKindness.objects.all()
        serializer = RandomActOfKindnessSerializer(rak_posts, many=True)
        return Response(serializer.data)

    def post(self, request):
            serializer = RandomActOfKindnessSerializer(data=request.data)
            if serializer.is_valid():
                # Set both creator and owner to the authenticated user
                serializer.save(creator=request.user, owner=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View for retrieving, updating, or deleting a specific RandomActOfKindness instance
class RandomActOfKindnessDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            rak_post = RandomActOfKindness.objects.get(pk=pk)
            self.check_object_permissions(self.request, rak_post)  # Check custom permissions
            return rak_post
        except RandomActOfKindness.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        rak_post = self.get_object(pk)
        serializer = RandomActOfKindnessSerializer(rak_post)
        return Response(serializer.data)

    def put(self, request, pk):
        rak_post = self.get_object(pk)
        serializer = RandomActOfKindnessSerializer(
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


# View for listing and creating RAKClaim instances
from rest_framework.permissions import IsAuthenticated

class RAKClaimList(APIView):
    # Require users to be authenticated to interact with this view
    permission_classes = [IsAuthenticated]  # This ensures only authenticated users can access this

    def get(self, request):
        claimed_raks = RAKClaim.objects.all()
        serializer = RAKClaimListSerializer(claimed_raks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RAKClaimListSerializer(data=request.data)
        if serializer.is_valid():
            rak = serializer.validated_data['rak']
            
            # Prevent the owner from claiming their own RAK
            if rak.creator == request.user:
                return Response({"error": "You cannot claim your own RAK."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Save the claim with the current user as the claimant
            claimed_rak = serializer.save(claimant=request.user)
            # Update the RandomActOfKindness status to 'claimed'
            claimed_rak.rak.status = 'claimed'
            claimed_rak.rak.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# View for retrieving, updating, or deleting a specific RAKClaim instance
class RAKClaimDetail(APIView):
    permission_classes = [IsClaimantOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(RAKClaim, pk=pk)

    def get(self, request, pk):
        claimed_rak = self.get_object(pk)
        serializer = RAKClaimSerializer(claimed_rak)
        return Response(serializer.data)

    def put(self, request, pk):
        claimed_rak = self.get_object(pk)
        serializer = RAKClaimSerializer(claimed_rak, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        claimed_rak = self.get_object(pk)
        claimed_rak.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    permission_classes = [IsAuthenticated]  # Only allow authenticated users

    def post(self, request, pk):
        original_rak = RandomActOfKindness.objects.get(pk=pk)

        try:
            # Try to get the claim associated with the RAK
            rak_claim = RAKClaim.objects.get(rak=original_rak)
            
            # Log details for debugging
            print(f"Claimant: {rak_claim.claimant}, Requesting User: {request.user}")

            # Check if the requesting user is the claimant
            if rak_claim.claimant != request.user:
                return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        except RAKClaim.DoesNotExist:
            return Response({"error": "This RAK has not been claimed yet."}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed only if the original RAK is completed
        if original_rak.completed_at:
            new_rak = RandomActOfKindness(
                creator=request.user,  # The person who pays it forward becomes the new creator
                description=request.data.get('description'),
                is_paid_forward=True
            )
            new_rak.save()
            original_rak.pay_it_forward()  # Mark the original RAK as paid forward
            return Response({'status': 'Pay It Forward created successfully'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Original RAK is not completed.'}, status=status.HTTP_400_BAD_REQUEST)




# View for handling claims on Random Acts of Kindness
class ClaimRAKView(APIView):
    def post(self, request, rak_id):
        try:
            rak = RandomActOfKindness.objects.get(id=rak_id)
            # Call the claim_rak method which includes the logic to check if it's still open
            rak.claim_rak(request.user)
            return Response({"message": "RAK claimed successfully."}, status=status.HTTP_200_OK)
        except RandomActOfKindness.DoesNotExist:
            return Response({"error": "RAK not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CompleteRAKView(APIView):
    def post(self, request, rak_id):
        try:
            rak = RandomActOfKindness.objects.get(id=rak_id)
            # Call the claim_rak method which includes the logic to check if it's still open
            rak.complete_rak(request.user)
            return Response({"message": "RAK claimed successfully."}, status=status.HTTP_200_OK)
        except RandomActOfKindness.DoesNotExist:
            return Response({"error": "RAK not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# class UpdateRAKStatusView(APIView):
#     permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]  # Only allow authenticated users and apply the permissions

#     def patch(self, request, pk):
#         # Retrieve the RAK object using the primary key (pk)
#         rak = get_object_or_404(RandomActOfKindness, pk=pk)

#         # Check if the user has permission to change the status
#         self.check_object_permissions(request, rak)

#         # Extract the new status from the request data
#         new_status = request.data.get('status')
        
#         if new_status:
#             # Update the status of the RAK
#             try:
#                 rak.update_status(new_status)
#                 return Response({"message": "Status updated successfully"}, status=status.HTTP_200_OK)
#             except ValueError as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#         return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)