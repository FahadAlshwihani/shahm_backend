# seo/serializers.py
from rest_framework import serializers
from .models import DefaultSEO, PageSEO


class DefaultSEOSerializer(serializers.ModelSerializer):
    og_image_url = serializers.SerializerMethodField()
    twitter_image_url = serializers.SerializerMethodField()

    class Meta:
        model = DefaultSEO
        fields = "__all__"

    def get_og_image_url(self, obj):
        return obj.og_image.url if obj.og_image else None

    def get_twitter_image_url(self, obj):
        return obj.twitter_image.url if obj.twitter_image else None


class PageSEOSerializer(serializers.ModelSerializer):
    og_image_url = serializers.SerializerMethodField()

    class Meta:
        model = PageSEO
        fields = "__all__"

    def get_og_image_url(self, obj):
        return obj.og_image.url if obj.og_image else None
