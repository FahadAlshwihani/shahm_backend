from rest_framework import serializers
from django.utils.text import slugify

from .models import PracticeArea, Service, ServiceAdvisoryPage, ServiceAdvisoryRequest, CareerJob, CareerApplication, ServiceAdvisoryRequestItem
from django.utils.text import slugify
from .client_files import Client, ClientFile
from services.utils import generate_reference
from cms.serializers import FAQItemSerializer
from cms.models import FAQItem


class PracticeAreaSerializer(serializers.ModelSerializer):
    services_count = serializers.SerializerMethodField()

    class Meta:
        model = PracticeArea
        fields = "__all__"
        extra_kwargs = {
            "slug": {"required": False},
            "is_active": {"required": False},
        }

    def get_services_count(self, obj):
        return obj.services.filter(is_active=True).count()

    def _generate_unique_slug(self, base_slug, instance_id=None):
        slug = base_slug
        counter = 1

        while Service.objects.filter(slug=slug).exclude(id=instance_id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def create(self, validated_data):
        if not validated_data.get("slug"):
            base_slug = slugify(
                validated_data.get("title_en") or validated_data.get("title_ar")
            )
            validated_data["slug"] = self._generate_unique_slug(base_slug)

        validated_data["is_active"] = True
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if not validated_data.get("slug"):
            base_slug = slugify(
                validated_data.get("title_en", instance.title_en)
                or validated_data.get("title_ar", instance.title_ar)
            )
            validated_data["slug"] = self._generate_unique_slug(
                base_slug,
                instance_id=instance.id
            )

        return super().update(instance, validated_data)

class ServiceSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False)

    practice_area = serializers.PrimaryKeyRelatedField(
        queryset=PracticeArea.objects.all(),
        required=True
    )

    faqs = serializers.PrimaryKeyRelatedField(
        queryset=FAQItem.objects.filter(is_active=True),
        many=True,
        required=False
    )

    faq_data = FAQItemSerializer(
        source="faqs",
        many=True,
        read_only=True
    )

    area_data = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = "__all__"

    def _generate_unique_slug(self, base_slug, instance_id=None):
        slug = base_slug
        counter = 1

        while Service.objects.filter(slug=slug).exclude(id=instance_id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def create(self, validated_data):
        base_slug = slugify(
            validated_data.get("title_en") or
            validated_data.get("title_ar")
        )

        validated_data["slug"] = self._generate_unique_slug(base_slug)
        validated_data["is_active"] = True

        return super().create(validated_data)

    def update(self, instance, validated_data):
        base_slug = slugify(
            validated_data.get("title_en", instance.title_en) or
            validated_data.get("title_ar", instance.title_ar)
        )

        validated_data["slug"] = self._generate_unique_slug(
            base_slug,
            instance_id=instance.id
        )

        return super().update(instance, validated_data)

    def get_area_data(self, obj):
        if not obj.practice_area:
            return None
        return {
            "id": obj.practice_area.id,
            "name_ar": obj.practice_area.name_ar,
            "name_en": obj.practice_area.name_en,
            "slug": obj.practice_area.slug,
        }


class ServiceAdvisoryPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAdvisoryPage
        fields = "__all__"


class ServiceMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "title_ar", "title_en"]


class ServiceAdvisoryRequestItemSerializer(serializers.ModelSerializer):

    service = ServiceMiniSerializer(read_only=True)

    class Meta:
        model = ServiceAdvisoryRequestItem
        fields = ["service"]



class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class ClientFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientFile
        fields = "__all__"

# =========================================================
# ================= CAREERS SERIALIZERS ===================
# =========================================================

class CareerJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerJob
        fields = "__all__"


class CareerApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title_ar", read_only=True)

    job_id = serializers.PrimaryKeyRelatedField(
        queryset=CareerJob.objects.all(),
        source="job",
        write_only=True,
        required=False
    )

    class Meta:
        model = CareerApplication
        fields = "__all__"

    def create(self, validated_data):
        obj = super().create(validated_data)
        obj.reference = generate_reference("career")
        obj.save()
        return obj


class ServiceAdvisoryRequestSerializer(serializers.ModelSerializer):

    items = ServiceAdvisoryRequestItemSerializer(many=True, read_only=True)

    service_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    class Meta:
        model = ServiceAdvisoryRequest
        fields = [
            "id",
            "title",
            "first_name",
            "last_name",
            "email",
            "phone",
            "message",
            "attachment",
            "voice_note",
            "service_ids",
            "items",
            "status",
            "created_at",
        ]

    def create(self, validated_data):

        service_ids = validated_data.pop("service_ids", [])

        obj = ServiceAdvisoryRequest.objects.create(**validated_data)

        for sid in service_ids:
            ServiceAdvisoryRequestItem.objects.create(
                request=obj,
                service_id=sid
            )

        obj.reference = generate_reference("service")
        obj.save()

        return obj
