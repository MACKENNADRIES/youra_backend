from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework import status
from django.http import Http404
from .models import RandomActOfKindness, RAKClaim, UserProfile, Block, User, PayItForward
from .serializers import RandomActOfKindnessSerializer, RAKClaimSerializer, ReportSerializer, CustomAuthTokenSerializer
from .permissions import IsOwnerOrClaimant
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
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrClaimant]

    def get_object(self, pk):
        try:
            rak_post = RandomActOfKindness.objects.get(pk=pk)
            self.check_object_permissions(self.request, rak_post)  # Check permissions
            return rak_post
        except RandomActOfKindness.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        rak_post = self.get_object(pk)

        # Check if the RAK is posted anonymously
        if rak_post.post_anonymously:
            rak_data = {
                'title': rak_post.title,
                'description': rak_post.description,
                'owner': 'Anonymous',  # Anonymize owner
                'aura_points': rak_post.aura_points,
                'status': rak_post.status,
            }
        else:
            rak_data = {
                'title': rak_post.title,
                'description': rak_post.description,
                'owner': rak_post.owner.username,  # Display owner's username
                'aura_points': rak_post.aura_points,
                'status': rak_post.status,
            }

        return Response(rak_data)

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

    def post(self, request):
        serializer = RAKClaimSerializer(data=request.data, context={'request': request})  # Add context for user
        if serializer.is_valid():
            try:
                # Save the claim using the serializer's create method
                claimed_rak = serializer.save()

                # Update the RandomActOfKindness status to 'claimed'
                claimed_rak.rak.status = 'claimed'
                claimed_rak.rak.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View for retrieving or updating a specific RAKClaim instance
class RAKClaimDetail(APIView):
    permission_classes = [IsOwnerOrClaimant]

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
            "aura_sub_level": user_profile.aura_sub_level,
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

class CreateReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(reporter=request.user)
            return Response({"message": "Report submitted successfully"}, status=201)
        return Response(serializer.errors, status=400)
    
class BlockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, blocked_user_id):
        blocked_user = get_object_or_404(User, id=blocked_user_id)
        Block.objects.create(user=request.user, blocked_user=blocked_user)
        return Response({"message": "User blocked successfully"}, status=201)


class LeaderboardView(APIView):
    def get(self, request):
        top_users = UserProfile.objects.order_by('-aura_points')[:10]
        data = [{
            'username': user.user.username,
            'aura_points': user.aura_points,
            'aura_level': user.aura_level,
        } for user in top_users]
        return Response(data, status=200)
    

class EnableCollaborationView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrClaimant]

    def post(self, request, rak_id):
        rak = get_object_or_404(RandomActOfKindness, id=rak_id)
        # Ensure that only the owner can enable collaboration
        if rak.owner != request.user:
            return Response({"error": "You do not have permission to enable collaboration on this RAK."}, status=403)

        rak.enable_collaborators()
        return Response({"message": "Collaboration has been enabled."}, status=200)

class JoinRAKView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, rak_id):
        rak = get_object_or_404(RandomActOfKindness, id=rak_id)
        
        if rak.status != 'completed':
            try:
                rak.add_collaborator(request.user)
                return Response({"message": "You have joined the RAK as a collaborator."}, status=201)
            except ValueError as e:
                return Response({"error": str(e)}, status=400)
        return Response({"error": "RAK is already completed."}, status=400)


class PayItForwardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, rak_id):
        original_rak = get_object_or_404(RandomActOfKindness, id=rak_id)

        # Ensure that the original RAK is completed before paying it forward
        if original_rak.status != 'completed':
            return Response({"error": "RAK must be completed before paying it forward."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure that this RAK has not already been paid forward
        if original_rak.is_paid_forward:
            return Response({"error": "This RAK has already been paid forward."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new RAK for the Pay It Forward
        new_rak_data = request.data
        new_rak = RandomActOfKindness.objects.create(
            creator=request.user,
            owner=request.user,
            title=new_rak_data.get('title', f"Pay It Forward for: {original_rak.title}"),
            description=new_rak_data.get('description', ''),
            aura_points=new_rak_data.get('aura_points', original_rak.aura_points),
        )

        # Mark original RAK as paid forward
        original_rak.is_paid_forward = True
        original_rak.save()

        # Create the Pay It Forward record
        PayItForward.objects.create(
            original_rak=original_rak,
            new_rak=new_rak,
            pay_it_forward_by=request.user,
        )

        serializer = RandomActOfKindnessSerializer(new_rak)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })