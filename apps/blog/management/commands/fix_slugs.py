from django.core.management.base import BaseCommand
from apps.blog.models import BlogPost
from django.utils.text import slugify


class Command(BaseCommand):
    help = "Fix missing slugs for blog posts"

    def handle(self, *args, **kwargs):
        counter = 1
        posts = BlogPost.objects.all()

        for p in posts:
            if not p.slug or str(p.slug).strip() == "":
                base_slug = slugify(p.title_en or p.title_ar) or f"post-{p.id}"
                new_slug = base_slug

                exists = BlogPost.objects.filter(slug=new_slug).exclude(id=p.id).exists()
                while exists:
                    counter += 1
                    new_slug = f"{base_slug}-{counter}"
                    exists = BlogPost.objects.filter(slug=new_slug).exclude(id=p.id).exists()

                p.slug = new_slug
                p.status = "published"
                p.save()
                self.stdout.write(self.style.SUCCESS(f"✔ Fixed: {p.id} → {new_slug}"))

        self.stdout.write(self.style.SUCCESS("✓ All slugs fixed successfully!"))
