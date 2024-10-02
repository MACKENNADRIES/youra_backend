from rest_framework import serializers
from .models import RAKPost, ClaimedRAK, ClaimAction

class RAKPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAKPost
        fields = '__all__'

class ClaimedRAKSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimedRAK
        fields = '__all__'

class ClaimActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimAction
        fields = '__all__'
