from django.contrib.auth import get_user_model
from rest_framework import serializers

from product_app.models import Document


class UserSerializer(serializers.ModelSerializer):
    is_related = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = 'id first_name last_name username user_type phone email is_related'.split()

    def get_is_related(self, obj):
        count = Document.objects.filter(user=obj).count()
        if count > 0:
            return True
        return False
