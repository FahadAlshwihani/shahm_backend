# team/serializers.py
from rest_framework import serializers
from .models import TeamMember, TeamPage, TeamCategory

class TeamCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamCategory
        fields = "__all__"


class TeamPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamPage
        fields = "__all__"


class TeamMemberSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = TeamMember
        fields = "__all__"

    def get_profile_image_url(self, obj):
        request = self.context.get("request")
        if obj.profile_image:
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None


