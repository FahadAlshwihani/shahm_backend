from rest_framework import serializers
from django.utils.html import strip_tags
from .models import Category, Tag, BlogPost, BlogPageSettings, BlogSection
from apps.accounts.serializers import UserSerializer
from django.utils.text import slugify
from django.utils.text import slugify


class CategorySerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = "__all__"

    def get_icon_url(self, obj):
        request = self.context.get("request")
        if not obj.icon:
            return None

        if request:
            return request.build_absolute_uri(obj.icon.url)

        return obj.icon.url  # fallback

    def create(self, validated_data):
        if not validated_data.get("slug"):
            validated_data["slug"] = slugify(validated_data.get("name_en") or validated_data.get("name_ar"))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "slug" not in validated_data or not validated_data.get("slug"):
            validated_data["slug"] = slugify(validated_data.get("name_en") or validated_data.get("name_ar"))
        return super().update(instance, validated_data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class BlogSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogSection
        fields = "__all__"


class BlogPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True
    )

    tags = TagSerializer(many=True, read_only=True)

    cover_image_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    sections = BlogSectionSerializer(many=True, read_only=True)
    sections_data = serializers.JSONField(write_only=True, required=False)

    read_time = serializers.IntegerField(read_only=True)

    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = BlogPost
        fields = "__all__"
        extra_kwargs = {"slug": {"required": False}}

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

    def validate_sections_data(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("sections_data must be a list")

        for section in value:
            if not section.get("title_ar") or not section.get("content_ar"):
                raise serializers.ValidationError("Each section must have title and content")

        return value

    # -------------------------
    # SLUG
    # -------------------------
    def generate_unique_slug(self, instance, title):
        MAX_SLUG_LENGTH = 50

        base = (slugify(title) or f"post-{instance.id}")[:MAX_SLUG_LENGTH]

        slug = base
        counter = 1

        while BlogPost.objects.filter(slug=slug).exclude(id=instance.id).exists():
            suffix = f"-{counter}"

            slug = (
                f"{base[:MAX_SLUG_LENGTH - len(suffix)]}{suffix}"
            )

            counter += 1

        return slug

    # -------------------------
    # CREATE
    # -------------------------
    def create(self, validated_data):
        tag_ids = validated_data.pop("tag_ids", [])
        sections_data = validated_data.pop("sections_data", [])

        if not sections_data:
            raise serializers.ValidationError({
                "sections_data": "At least one section is required"
            })

        cover = validated_data.pop("cover_image", None)
        image = validated_data.pop("image", None)

        # SEO
        if not validated_data.get("seo_title"):
            validated_data["seo_title"] = (
                    validated_data.get("title_en") or validated_data.get("title_ar")
            )

        if not validated_data.get("seo_description"):
            content = validated_data.get("intro_en") or validated_data.get("intro_ar")
            validated_data["seo_description"] = strip_tags(content)[:160] if content else ""

        post = BlogPost.objects.create(**validated_data)

        post.slug = self.generate_unique_slug(
            post,
            validated_data.get("title_en") or validated_data.get("title_ar")
        )

        if cover:
            post.cover_image = cover

        if image:
            post.image = image

        post.save()

        post.tags.set(tag_ids)

        for section in sections_data:
            BlogSection.objects.create(
                post=post,
                title_ar=section.get("title_ar", ""),
                title_en=section.get("title_en", ""),
                content_ar=section.get("content_ar", ""),
                content_en=section.get("content_en", ""),
                order=section.get("order", 0),
            )

        return post

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, instance, validated_data):
        tag_ids = validated_data.pop("tag_ids", None)
        sections_data = validated_data.pop("sections_data", None)

        cover = validated_data.pop("cover_image", None)
        image = validated_data.pop("image", None)

        # slug update
        if "title_ar" in validated_data or "title_en" in validated_data:
            title = (
                    validated_data.get("title_en", instance.title_en)
                    or validated_data.get("title_ar", instance.title_ar)
            )
            instance.slug = self.generate_unique_slug(instance, title)

        # SEO
        if not validated_data.get("seo_title"):
            validated_data["seo_title"] = (
                    validated_data.get("title_en") or validated_data.get("title_ar")
            )

        if not validated_data.get("seo_description"):
            content = validated_data.get("intro_en") or validated_data.get("intro_ar")
            validated_data["seo_description"] = strip_tags(content)[:160] if content else ""

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if cover:
            instance.cover_image = cover

        if image:
            instance.image = image

        instance.save()

        if tag_ids is not None:
            instance.tags.set(tag_ids)

        if sections_data is not None:
            instance.sections.all().delete()

            for section in sections_data:
                BlogSection.objects.create(
                    post=instance,
                    title_ar=section.get("title_ar", ""),
                    title_en=section.get("title_en", ""),
                    content_ar=section.get("content_ar", ""),
                    content_en=section.get("content_en", ""),
                    order=section.get("order", 0),
                )

        return instance


class BlogPageSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPageSettings
        fields = "__all__"
