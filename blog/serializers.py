from rest_framework import serializers
from .models import Category, Tag, BlogPost, BlogPageSettings, BlogClause, BlogRelatedPerson
from accounts.serializers import UserSerializer
from django.utils.text import slugify


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class BlogClauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogClause
        fields = "__all__"


class BlogRelatedPersonSerializer(serializers.ModelSerializer):

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogRelatedPerson
        fields = "__all__"

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class BlogPostSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)
    category_data = CategorySerializer(source="category", read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    cover_image_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    clauses = BlogClauseSerializer(many=True, read_only=True)
    read_time = serializers.IntegerField(read_only=True)

    related_people = BlogRelatedPersonSerializer(many=True, read_only=True)
    related_people_data = serializers.JSONField(write_only=True, required=False)

    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    clauses_data = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = BlogPost
        fields = "__all__"
        extra_kwargs = {"slug": {"required": False}}

    # -------------------------
    # SAFE URL BUILDER
    # -------------------------
    def _build_url(self, field):
        request = self.context.get("request")
        if not field:
            return None
        if request:
            return request.build_absolute_uri(field.url)
        return field.url

    def get_cover_image_url(self, obj):
        return self._build_url(obj.cover_image)

    def get_image_url(self, obj):
        return self._build_url(obj.image)

    # -------------------------
    # UNIQUE SLUG
    # -------------------------
    def generate_unique_slug(self, instance, title):
        base = slugify(title) or f"post-{instance.id}"
        slug = base
        counter = 1

        while BlogPost.objects.filter(slug=slug).exclude(id=instance.id).exists():
            slug = f"{base}-{counter}"
            counter += 1

        return slug

    # ======================================================
    # CREATE
    # ======================================================
    def create(self, validated_data):

        tag_ids = validated_data.pop("tag_ids", [])
        clauses_data = validated_data.pop("clauses_data", [])

        category = validated_data.pop("category", None)
        cover = validated_data.pop("cover_image", None)
        image = validated_data.pop("image", None)

        request = self.context["request"]

        post = BlogPost.objects.create(**validated_data)

        if category:
            post.category_id = category.id if hasattr(category, "id") else category

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

        # =========================
        # CLAUSES
        # =========================
        for clause in clauses_data:
            BlogClause.objects.create(
                post=post,
                title_ar=clause.get("title_ar", ""),
                title_en=clause.get("title_en", ""),
                content_ar=clause.get("content_ar", ""),
                content_en=clause.get("content_en", ""),
                order=clause.get("order", 0)
            )

        # =========================
        # RELATED PEOPLE
        # =========================

        index = 0
        while True:
            name_ar = request.data.get(f"related_people_data[{index}][name_ar]")
            if not name_ar:
                break

            image = request.FILES.get(f"related_people_data[{index}][image]")

            BlogRelatedPerson.objects.create(
                post=post,
                name_ar=name_ar,
                name_en=request.data.get(f"related_people_data[{index}][name_en]", ""),
                description_ar=request.data.get(f"related_people_data[{index}][description_ar]", ""),
                description_en=request.data.get(f"related_people_data[{index}][description_en]", ""),
                order=request.data.get(f"related_people_data[{index}][order]", 0),
                image=image
            )

            index += 1

        return post

    # ======================================================
    # UPDATE
    # ======================================================
    def update(self, instance, validated_data):
        tag_ids = validated_data.pop("tag_ids", None)
        category = validated_data.pop("category", None)
        clauses_data = validated_data.pop("clauses_data", None)

        cover = validated_data.pop("cover_image", None)
        image = validated_data.pop("image", None)
        related_people_data = validated_data.pop("related_people_data", None)


        request = self.context["request"]

        if any(key.startswith("related_people_data") for key in request.data.keys()):

            instance.related_people.all().delete()

            index = 0
            while True:
                name_ar = request.data.get(f"related_people_data[{index}][name_ar]")
                if not name_ar:
                    break

                image = request.FILES.get(f"related_people_data[{index}][image]")

                BlogRelatedPerson.objects.create(
                    post=instance,
                    name_ar=name_ar,
                    name_en=request.data.get(f"related_people_data[{index}][name_en]", ""),
                    description_ar=request.data.get(f"related_people_data[{index}][description_ar]", ""),
                    description_en=request.data.get(f"related_people_data[{index}][description_en]", ""),
                    order=request.data.get(f"related_people_data[{index}][order]", 0),
                    image=image
                )

                index += 1

        # لو تغير العنوان نعيد بناء slug
        if "title_ar" in validated_data or "title_en" in validated_data:
            title = (
                validated_data.get("title_en", instance.title_en)
                or validated_data.get("title_ar", instance.title_ar)
            )
            instance.slug = self.generate_unique_slug(instance, title)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # تحديث التصنيف
        if category is not None:
            instance.category_id = (
                category.id if hasattr(category, "id") else category
            )

        if cover:
            instance.cover_image = cover
        if image:
            instance.image = image

        instance.save()

        if tag_ids is not None:
            instance.tags.set(tag_ids)

        if clauses_data is not None:
            instance.clauses.all().delete()

            for clause in clauses_data:
                BlogClause.objects.create(
                    post=instance,
                    title_ar=clause.get("title_ar", ""),
                    title_en=clause.get("title_en", ""),
                    content_ar=clause.get("content_ar", ""),
                    content_en=clause.get("content_en", ""),
                    order=clause.get("order", 0)
                )

        return instance


class BlogPageSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPageSettings
        fields = "__all__"

class PublicRelatedPersonSerializer(serializers.ModelSerializer):

    image_url = serializers.SerializerMethodField()

    class Meta:
        model = BlogRelatedPerson
        fields = [
            "id",
            "name_ar",
            "name_en",
            "description_ar",
            "description_en",
            "image_url",
            "order"
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if not obj.image:
            return None
        return request.build_absolute_uri(obj.image.url)




