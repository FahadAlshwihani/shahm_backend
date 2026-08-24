from rest_framework import serializers
from .serializers import CategorySerializer, TagSerializer
from django.utils.html import strip_tags
from .models import BlogPost, BlogSection


class PublicSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogSection
        fields = "__all__"


class PublicBlogPostSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    excerpt_ar = serializers.SerializerMethodField()
    excerpt_en = serializers.SerializerMethodField()
    sections = PublicSectionSerializer(many=True, read_only=True)
    read_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "slug",
            "title_ar",
            "title_en",
            "intro_ar",  # ✅ FIX
            "intro_en",  # ✅ FIX
            "excerpt_ar",
            "excerpt_en",
            "cover_image_url",
            "image_url",
            "created_at",
            "views_count",
            "category",
            "tags",
            "read_time",
            "sections",
        ]

    def _build_url(self, field):
        request = self.context.get("request")
        if not field:
            return None
        return request.build_absolute_uri(field.url) if request else field.url

    def get_cover_image_url(self, obj):
        return self._build_url(obj.cover_image)

    def get_image_url(self, obj):
        return self._build_url(obj.image)

    def get_excerpt_ar(self, obj):
        if obj.intro_ar:  # ✅ FIX
            return strip_tags(obj.intro_ar)[:160]
        return ""

    def get_excerpt_en(self, obj):
        if obj.intro_en:  # ✅ FIX
            return strip_tags(obj.intro_en)[:160]
        return ""
