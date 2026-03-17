from rest_framework import serializers
from .models import LegalPage, LegalSection


class LegalSectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = LegalSection
        fields = [
            "id",
            "title_ar",
            "title_en",
            "content_ar",
            "content_en",
            "anchor",
            "order",
        ]


class LegalPageSerializer(serializers.ModelSerializer):

    sections = LegalSectionSerializer(many=True, read_only=True)
    sections_data = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = LegalPage
        fields = "__all__"

    def validate(self, data):

        sections = data.get("sections_data")

        if sections is not None and len(sections) == 0:
            raise serializers.ValidationError(
                "Legal page must contain at least one section."
            )

        return data


    def create(self, validated_data):

        sections_data = validated_data.pop("sections_data", [])

        page = LegalPage.objects.create(**validated_data)

        for index, section in enumerate(sections_data):

            LegalSection.objects.create(
                page=page,
                title_ar=section.get("title_ar"),
                title_en=section.get("title_en"),
                content_ar=section.get("content_ar"),
                content_en=section.get("content_en"),
                order=index
            )

        return page


    def update(self, instance, validated_data):

        sections_data = validated_data.pop("sections_data", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if sections_data is not None:

            # حذف القديم
            instance.sections.all().delete()

            # إنشاء الجديد بالترتيب
            for index, section in enumerate(sections_data):

                LegalSection.objects.create(
                    page=instance,
                    title_ar=section.get("title_ar"),
                    title_en=section.get("title_en"),
                    content_ar=section.get("content_ar"),
                    content_en=section.get("content_en"),
                    order=index
                )

        return instance

class PublicLegalPageSerializer(serializers.ModelSerializer):

    sections = LegalSectionSerializer(many=True)

    class Meta:
        model = LegalPage
        fields = [
            "slug",
            "title_ar",
            "title_en",
            "meta_title_ar",
            "meta_title_en",
            "meta_description_ar",
            "meta_description_en",
            "sections",
            "updated_at",
            "last_updated"
        ]