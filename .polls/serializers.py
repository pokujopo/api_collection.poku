from rest_framework import serializers
from .models import Test
"""
class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'name', 'link', 'status', 'created_at'] # User hatomuweka hapa, atasaviwa kiotomatiki kama yupo
"""

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'link', 'format_type', 'quality', 'status', 'name', 'error_message']
        read_only_fields = ['id', 'status', 'name']

    # Validation ya dharura kuhakikisha link sio feki
    def validate_link(self, value):
        if "youtube.com" not in value and "youtu.be" not in value and "facebook.com" not in value:
            raise serializers.ValidationError("Link inayokubalika ni ya YouTube au Facebook pekee!")
        return value