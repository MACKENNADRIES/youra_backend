from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework import status
from django.http import Http404
from .models import RandomActOfKindness, RAKClaim, UserProfile
from .serializers import RandomActOfKindnessSerializer, RAKClaimSerializer
from .permissions import IsOwnerOrReadOnly, IsClaimantOrReadOnly
from rest_framework.permissions import IsAuthenticated

# View for listing and creating Random Acts of Kindness
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


# View for retrieving, updating (status, claiming, completing), or deleting a specific RAK
class RandomActOfKindnessDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            rak_post = RandomActOfKindness.objects.get(pk=pk)
            self.check_object_permissions(self.request, rak_post)  # Check permissions
            return rak_post
        except RandomActOfKindness.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        rak_post = self.get_object(pk)
        serializer = RandomActOfKindnessSerializer(rak_post)
        return Response(serializer.data)

    def put(self, request, pk):
        rak_post = self.get_object(pk)
        status_update = request.data.get("status")

        if status_update == 'claimed':
            rak_post.claim_rak(request.user)  # Handle claiming logic here
        elif status_update == 'in_progress':
            rak_post.status = 'in_progress'  # Update status to in progress
        elif status_update == 'completed':
            rak_post.complete_rak()  # Handle completion logic here
        elif status_update == 'pay_it_forward':
            rak_post.pay_it_forward()  # Handle pay it forward logic here
        else:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        rak_post.save()
        serializer = RandomActOfKindnessSerializer(rak_post)
        return Response(serializer.data)

    def delete(self, request, pk):
        rak_post = self.get_object(pk)
        rak_post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# View for listing and creating RAKClaim instances
class RAKClaimList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        claimed_raks = RAKClaim.objects.all()
        serializer = RAKClaimSerializer(claimed_raks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RAKClaimSerializer(data=request.data)
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


# View for retrieving or updating a specific RAKClaim instance
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


# View for retrieving user profile information
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        data = {
            "username": request.user.username,
            "email": request.user.email,
            "aura_points": user_profile.aura_points,
            "aura_level": user_profile.aura_level,
            "aura_color": user_profile.aura_color
        }
        return Response(data, status=200)


# Admin-only view for listing all user profiles
class UserProfileListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        profiles = UserProfile.objects.all()
        data = [
            {
                "username": profile.user.username,
                "email": profile.user.email,
                "aura_points": profile.aura_points,
                "aura_level": profile.aura_level,
                "aura_color": profile.aura_color
            }
            for profile in profiles
        ]
        return Response(data, status=200)
