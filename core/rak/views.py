# rak/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, Http404
from .models import RandomActOfKindness, PayItForward
from .serializers import (
    RandomActOfKindnessSerializer,
    PayItForwardSerializer,
)  # Remove PayItForwardSerializer
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .permissions import IsOwnerOrClaimant


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


class RandomActOfKindnessDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrClaimant]

    def get_object(self, pk):
        try:
            rak_post = RandomActOfKindness.objects.get(pk=pk)
            self.check_object_permissions(self.request, rak_post)
            return rak_post
        except RandomActOfKindness.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        rak_post = self.get_object(pk)

        list_claims = request.query_params.get(
            "list_claims", ""
        ).lower()  # Get and convert to lowercase
        if list_claims:
            claims = rak_post.claims.all()
            claims_data = [
                {
                    "claimer": claim.claimant.username,
                    "claimed_at": claim.claimed_at,
                    "status": rak_post.status,
                }
                for claim in claims
            ]
            return Response(claims_data, status=status.HTTP_200_OK)
        if rak_post.post_anonymously:
            rak_data = {
                "title": rak_post.title,
                "description": rak_post.description,
                "owner": "Anonymous",
                "aura_points": rak_post.aura_points,
                "status": rak_post.status,
            }
        else:
            rak_data = {
                "title": rak_post.title,
                "description": rak_post.description,
                "owner": rak_post.owner.username,
                "aura_points": rak_post.aura_points,
                "status": rak_post.status,
            }
        return Response(rak_data)

    def put(self, request, pk):
        rak_post = self.get_object(pk)

        # Check if the request is for updating the post details (title, description, media)
        if (
            "title" in request.data
            or "description" in request.data
            or "media" in request.data
        ):
            serializer = RandomActOfKindnessSerializer(
                rak_post, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Handle status update logic
        status_update = request.data.get("status")

        if status_update == "claimed":
            try:
                rak_post.claim_rak(request.user)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif status_update == "in_progress":
            rak_post.status = "in_progress"
            rak_post.save()
        elif status_update == "completed":
            try:
                rak_post.complete_rak()
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif status_update == "pay_it_forward":
            return Response(
                {"error": "Use the pay_it_forward endpoint."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return Response(
                {"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RandomActOfKindnessSerializer(rak_post)
        return Response(serializer.data)

    def delete(self, request, pk):
        rak_post = self.get_object(pk)
        rak_post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# class RAKClaimList(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = RAKClaimSerializer(data=request.data, context={"request": request})

#         if serializer.is_valid():
#             rak = RandomActOfKindness.objects.get(
#                 id=serializer.validated_data["rak"].id
#             )

#             # Check if the RAK allows multiple claimants
#             if (
#                 not rak.allow_collaborators and rak.claims.exists()
#             ):  # Use 'claims' related_name
#                 return Response(
#                     {"error": "This RAK has already been claimed."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )

#             try:
#                 claimed_rak = serializer.save(claimant=request.user)
#                 rak.status = "in_progress"  # Update RAK status to 'in_progress'
#                 rak.save()

#                 return Response(serializer.data, status=status.HTTP_201_CREATED)

#             except Exception as e:
#                 return Response(
#                     {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class RAKClaimDetail(APIView):
#     permission_classes = [IsOwnerOrClaimant]

#     def get_object(self, pk):
#         return get_object_or_404(RAKClaim, pk=pk)

#     def get(self, request, pk):
#         claimed_rak = self.get_object(pk)
#         serializer = RAKClaimSerializer(claimed_rak)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         claimed_rak = self.get_object(pk)
#         serializer = RAKClaimSerializer(claimed_rak, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         claimed_rak = self.get_object(pk)
#         claimed_rak.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class EnableCollaborationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, rak_id):
        rak_post = get_object_or_404(RandomActOfKindness, id=rak_id)
        if rak_post.creator != request.user:
            return Response(
                {"error": "Only the creator can enable collaboration."}, status=403
            )
        rak_post.enable_collaborators()
        return Response({"message": "Collaboration enabled."})


class JoinRAKView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, rak_id):
        rak = get_object_or_404(RandomActOfKindness, id=rak_id)
        if request.user not in rak.collaborators.all():
            rak.collaborators.add(request.user)
            rak.save()
            return Response(
                {"message": "You have joined as a collaborator."}, status=201
            )
        return Response({"error": "You are already a collaborator."}, status=400)


class PayItForwardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, rak_id):
        original_rak = get_object_or_404(RandomActOfKindness, id=rak_id)

        # Ensure that the original RAK is completed before paying it forward
        if original_rak.status != "completed":
            return Response(
                {"error": "RAK must be completed before paying it forward."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure that this RAK has not already been paid forward
        if original_rak.is_paid_forward:
            return Response(
                {"error": "This RAK has already been paid forward."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a new RAK for the Pay It Forward
        new_rak_data = request.data
        new_rak = RandomActOfKindness.objects.create(
            creator=request.user,
            owner=request.user,
            title=new_rak_data.get(
                "title", f"Pay It Forward for: {original_rak.title}"
            ),
            description=new_rak_data.get("description", ""),
            aura_points=new_rak_data.get("aura_points", original_rak.aura_points),
            post_type="offer",  # Automatically set post_type to 'offer' for Pay It Forward
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

        # Award aura points to the original requester (the owner of the original RAK)
        if original_rak.post_type == "request":
            user_profile = original_rak.owner.userprofile
            aura_points_for_requester = (
                original_rak.aura_points
            )  # Award full points to the requester
            user_profile.aura_points += aura_points_for_requester
            user_profile.calculate_level()
            user_profile.save()

        serializer = RandomActOfKindnessSerializer(new_rak)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# List all PayItForward instances or create a new one
class PayItForwardListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pay_it_forward_instances = PayItForward.objects.all()
        serializer = PayItForwardSerializer(pay_it_forward_instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PayItForwardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(pay_it_forward_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Retrieve, update, or delete a specific PayItForward instance
class PayItForwardDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        pay_it_forward_instance = get_object_or_404(PayItForward, pk=pk)
        serializer = PayItForwardSerializer(pay_it_forward_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        pay_it_forward_instance = get_object_or_404(PayItForward, pk=pk)
        serializer = PayItForwardSerializer(
            pay_it_forward_instance, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        pay_it_forward_instance = get_object_or_404(PayItForward, pk=pk)
        pay_it_forward_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# views.py
class UpdateRAKPostView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsOwnerOrClaimant,
    ]  # Ensure proper permissions

    def put(self, request, pk):
        # Get the RAK post by ID
        rak_post = get_object_or_404(RandomActOfKindness, pk=pk)

        # Ensure only the owner can edit the RAK post
        if rak_post.owner != request.user:
            return Response(
                {"error": "You don't have permission to edit this RAK."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Update only allowed fields
        data = request.data
        rak_post.title = data.get("title", rak_post.title)
        rak_post.description = data.get("description", rak_post.description)
        rak_post.visibility = data.get("visibility", rak_post.visibility)
        rak_post.post_type = data.get("post_type", rak_post.post_type)

        # Handle image removal if requested
        if data.get("remove_image", False):
            rak_post.media.delete(save=False)  # Delete the image from storage
            rak_post.media = None  # Set the media field to null

        # Handle new image upload if provided
        if "media" in request.FILES:
            rak_post.media = request.FILES["media"]  # Save the new image

        # Save the changes
        rak_post.save()

        # Return the updated post data
        serializer = RandomActOfKindnessSerializer(rak_post)
        return Response(serializer.data, status=status.HTTP_200_OK)
