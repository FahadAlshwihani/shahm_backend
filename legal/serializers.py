from django.db import transaction
from rest_framework import serializers
from .models import LegalPage, LegalSection, LegalSubSection


class LegalSubSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalSubSection
        fields = [
            "id",
            "title_ar",
            "title_en",
            "content_ar",
            "content_en",
            "order",
        ]


class LegalSectionSerializer(serializers.ModelSerializer):
    subsections = LegalSubSectionSerializer(many=True, read_only=True)

    class Meta:
        model = LegalSection
        fields = [
            "id",
            "title_ar",
            "title_en",
            "anchor",
            "order",
            "subsections",
        ]


class LegalPageSerializer(serializers.ModelSerializer):
    sections = LegalSectionSerializer(many=True, read_only=True)
    sections_data = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = LegalPage
        fields = "__all__"

    def validate(self, data):
        sections = data.get("sections_data")

        if sections is not None:
            if not sections:
                raise serializers.ValidationError(
                    {"sections_data": "Legal page must contain at least one section."}
                )

            for index, section in enumerate(sections):
                if not section.get("title_ar") or not section.get("title_en"):
                    raise serializers.ValidationError(
                        {"sections_data": f"Section #{index + 1} must have Arabic and English titles."}
                    )

                subsections = section.get("subsections", [])
                if not subsections:
                    raise serializers.ValidationError(
                        {"sections_data": f"Section #{index + 1} must contain at least one subsection."}
                    )

                for sub_index, sub in enumerate(subsections):
                    if not sub.get("title_ar") or not sub.get("title_en") or not sub.get("content_ar") or not sub.get(
                            "content_en"):
                        raise serializers.ValidationError(
                            {
                                "sections_data": (
                                    f"Subsection #{sub_index + 1} in section #{index + 1} "
                                    "must have Arabic and English titles."
                                )
                            }
                        )

        return data

    def _sync_sections(self, page, sections_data):
        page.sections.all().delete()

        for s_index, section in enumerate(sections_data):
            sec = LegalSection.objects.create(
                page=page,
                title_ar=section.get("title_ar"),
                title_en=section.get("title_en"),
                anchor=section.get("anchor", ""),
                order=section.get("order", s_index),
            )

            for sub_index, sub in enumerate(section.get("subsections", [])):
                LegalSubSection.objects.create(
                    section=sec,
                    title_ar=sub.get("title_ar"),
                    title_en=sub.get("title_en"),
                    content_ar=sub.get("content_ar", ""),
                    content_en=sub.get("content_en", ""),
                    order=sub.get("order", sub_index),
                )

    @transaction.atomic
    def create(self, validated_data):
        sections_data = validated_data.pop("sections_data", [])
        page = LegalPage.objects.create(**validated_data)
        self._sync_sections(page, sections_data)
        return page

    @transaction.atomic
    def update(self, instance, validated_data):
        sections_data = validated_data.pop("sections_data", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if sections_data is not None:
            self._sync_sections(instance, sections_data)

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
            "last_updated",
        ]
