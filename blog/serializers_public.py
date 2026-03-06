from rest_framework import serializers
from .models import BlogPost
from .serializers import CategorySerializer, TagSerializer, PublicRelatedPersonSerializer
from django.utils.html import strip_tags
from .models import BlogClause



class PublicClauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogClause
        fields = [
            "id",
            "title_ar",
            "title_en",
            "content_ar",
            "content_en",
            "order",
        ]


class PublicBlogPostSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    cover_image_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    excerpt_ar = serializers.SerializerMethodField()
    excerpt_en = serializers.SerializerMethodField()

    clauses = PublicClauseSerializer(many=True, read_only=True)
    read_time = serializers.IntegerField(read_only=True)

    related_people = PublicRelatedPersonSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "slug",
            "title_ar",
            "title_en",
            "content_ar",
            "content_en",
            "excerpt_ar",
            "excerpt_en",
            "cover_image_url",
            "image_url",
            "created_at",
            "views_count",
            "category",
            "tags",
            "read_time",
            "clauses",
            "related_people",
        ]

    # -------------------------
    # URL BUILDER
    # -------------------------
    def _build_url(self, field):
        request = self.context.get("request")
        if not field:
            return None
        return request.build_absolute_uri(field.url) if request else field.url

    def get_cover_image_url(self, obj):
        return self._build_url(obj.cover_image)

    def get_image_url(self, obj):
        return self._build_url(obj.image)

    # -------------------------
    # EXCERPT (AUTO)
    # -------------------------
    def get_excerpt_ar(self, obj):
        if obj.content_ar:
            return strip_tags(obj.content_ar)[:160]
        return ""

    def get_excerpt_en(self, obj):
        if obj.content_en:
            return strip_tags(obj.content_en)[:160]
        return ""


