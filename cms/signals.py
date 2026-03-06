from django.db.models.signals import post_migrate
from django.dispatch import receiver

from cms.models import FooterColumn, FooterLink, HeaderLink, Page
from core.models import SystemSeed

def upsert_link(*, column, label_ar, label_en, page=None, url="", order=0, parent=None):
    obj, created = FooterLink.objects.get_or_create(
        column=column,
        label_ar=label_ar,
        parent=parent,
        defaults={
            "label_en": label_en,
            "page": page,
            "url": "",
            "order": order,
            "is_active": True,
        },
    )

    changed = False

    if obj.label_en != label_en:
        obj.label_en = label_en
        changed = True

    if obj.page != page:
        obj.page = page
        changed = True

    if obj.url:
        obj.url = ""
        changed = True

    if obj.order != order:
        obj.order = order
        changed = True

    if obj.parent_id != (parent.id if parent else None):
        obj.parent = parent
        changed = True

    if changed:
        obj.save()

    return obj


@receiver(post_migrate)
def create_default_header(sender, **kwargs):
    if sender.name != "cms":
        return

    if SystemSeed.objects.filter(key="default_header_v1").exists():
        return

    default_links = [
        ("الصفحة الرئيسية", "Home", "/", 0),
        ("عن شهم", "About", "/page/about", 1),
        ("خدماتنا", "Services", "/services", 2),
        ("المقالات", "Blog", "/blog", 3),
    ]

    for ar, en, url, order in default_links:
        obj, _ = HeaderLink.objects.get_or_create(
            label_ar=ar,
            defaults={
                "label_en": en,
                "url": url,
                "order": order,
                "is_active": True,
                "type": "link",
            }
        )

        if not obj.type:
            obj.type = "link"
            obj.save()

    SystemSeed.objects.create(key="default_header_v1")


@receiver(post_migrate)
def create_default_pages(sender, **kwargs):
    if sender.name != "cms":
        return

    if SystemSeed.objects.filter(key="default_pages_v1").exists():
        return

    pages = [
        # خدمات العملاء
        ("appointments", "المواعيد والاستشارات", "Appointments & Consultations"),
        ("faq", "الأسئلة الشائعة", "FAQ"),
        ("contact-methods", "طرق التواصل", "Contact Methods"),

        # عن شهم
        ("about", "نبذة عنا", "About Us"),
        ("team", "فريق العمل", "Team"),
        ("practice-areas", "المجالات والقطاعات", "Practice Areas"),
        ("blog", "المقالات", "Blog"),
        ("news", "الأخبار والرؤى", "News & Insights"),

        # الأخلاقيات
        ("professional-charter", "ميثاق الامتثال المهني", "Professional Charter"),
        ("code-of-conduct", "نظام السلوك المهني", "Code of Conduct"),
        ("confidentiality-rules", "قواعد سرية المعلومات", "Confidentiality Rules"),

        # الوظائف
        ("careers-join", "الانضمام إلى الفريق", "Join the Team"),
        ("careers-internship", "التدريب القانوني", "Legal Internship"),
        ("careers-partners", "برنامج المتعاونين الخارجيين", "External Partners"),

        # الشروط
        ("terms", "الشروط والأحكام", "Terms & Conditions"),
        ("privacy-policy", "سياسة الخصوصية", "Privacy Policy"),
        ("info-confidentiality", "سياسة سرية المعلومات", "Info Confidentiality"),
        ("data-consent-disclaimer", "إخلاء المسؤولية عن موافقة خصوصية البيانات", "Data Consent Disclaimer"),
        ("cookies-policy", "سياسة ملفات تعريف الارتباط", "Cookies Policy"),
        ("service-advisory", "سياسة تقديم الاستشارات الخدمات", "Service Advisory"),
    ]

    for slug, ar, en in pages:
        Page.objects.get_or_create(
            slug=slug,
            defaults={
                "title_ar": ar,
                "title_en": en,
                "content_ar": f"محتوى تجريبي لصفحة {ar}",
                "content_en": f"Sample content for {en}",
                "is_published": True,
                "show_in_sitemap": True,
            },
        )

    SystemSeed.objects.create(key="default_pages_v1")


# ================= FOOTER =================
@receiver(post_migrate)
def create_default_footer(sender, **kwargs):
    if sender.name != "cms":
        return

    if SystemSeed.objects.filter(key="default_footer_v2").exists():
        return

    cols = {
        "newsletter": FooterColumn.objects.get_or_create(
            key="newsletter",
            defaults={
                "title_ar": "أرغب في تلقّي كل جديد من أخبار شهم",
                "title_en": "Newsletter",
                "order": 0,
                "is_active": True,
            },
        )[0],

        "about": FooterColumn.objects.get_or_create(
            key="about",
            defaults={
                "title_ar": "عن شهم",
                "title_en": "About Shahm",
                "order": 1,
                "is_active": True,
            },
        )[0],

        "customers": FooterColumn.objects.get_or_create(
            key="customers",
            defaults={
                "title_ar": "خدمات العملاء",
                "title_en": "customers",
                "order": 2,
                "is_active": True,
            },
        )[0],

        "ethics": FooterColumn.objects.get_or_create(
            key="ethics",
            defaults={
                "title_ar": "الأخلاقيات والامتثال",
                "title_en": "ethics",
                "order": 3,
                "is_active": True,
            },
        )[0],

        "legal": FooterColumn.objects.get_or_create(
            key="legal",
            defaults={
                "title_ar": "الشروط القانونية",
                "title_en": "legal",
                "order": 4,
                "is_active": True,
            },
        )[0],

        "sitemap": FooterColumn.objects.get_or_create(
            key="sitemap",
            defaults={
                "title_ar": "خريطة الموقع",
                "title_en": "sitemap",
                "order": 5,
                "is_active": True,
            },
        )[0],

        "follow": FooterColumn.objects.get_or_create(
            key="follow",
            defaults={
                "title_ar": "تابعنا",
                "title_en": "Follow Us",
                "order": 6,
                "is_active": True,
            },
        )[0],

    }

    # ================= ABOUT SHAHM =================
    about_root = upsert_link(
        column=cols["about"],
        label_ar="نبذة عنا",
        label_en="About Us",
        order=0
    )

    # Pages
    team_page = Page.objects.get(slug="team")
    practice_areas_page = Page.objects.get(slug="practice-areas")
    blog_page = Page.objects.get(slug="blog")
    news_page = Page.objects.get(slug="news")

    upsert_link(
        column=cols["about"],
        parent=about_root,
        label_ar="فريق العمل",
        label_en="Team",
        page=team_page,
        order=0
    )

    upsert_link(
        column=cols["about"],
        parent=about_root,
        label_ar="المجالات والقطاعات",
        label_en="Practice Areas",
        page=practice_areas_page,
        order=1
    )

    upsert_link(
        column=cols["about"],
        label_ar="المقالات",
        label_en="Blog",
        page=blog_page,
        order=1
    )

    upsert_link(
        column=cols["about"],
        label_ar="الأخبار والرؤى",
        label_en="News & Insights",
        page=news_page,
        order=2
    )

    # ================= CAREERS =================
    careers_root = upsert_link(
        column=cols["about"],
        label_ar="الوظائف",
        label_en="Careers",
        order=2
    )

    join_page = Page.objects.get(slug="careers-join")
    internship_page = Page.objects.get(slug="careers-internship")
    partners_page = Page.objects.get(slug="careers-partners")

    upsert_link(
        column=cols["about"],
        parent=careers_root,
        label_ar="الانضمام إلى الفريق",
        label_en="Join Team",
        page=join_page,
        order=0
    )

    upsert_link(
        column=cols["about"],
        parent=careers_root,
        label_ar="التدريب القانوني",
        label_en="Legal Internship",
        page=internship_page,
        order=1
    )

    upsert_link(
        column=cols["about"],
        parent=careers_root,
        label_ar="برنامج المتعاونين الخارجيين",
        label_en="External Partners",
        page=partners_page,
        order=2
    )

    # ================= CUSTOMER SERVICES =================
    appointments_page = Page.objects.get(slug="appointments")
    faq_page = Page.objects.get(slug="faq")
    contact_methods_page = Page.objects.get(slug="contact-methods")
    service_request_page = Page.objects.get(slug="service-advisory")  # عدّل لو slug مختلف

    upsert_link(
        column=cols["customers"],
        label_ar="حجز موعد",
        label_en="Book Appointment",
        page=appointments_page,
        order=0
    )

    upsert_link(
        column=cols["customers"],
        label_ar="طلب خدمة قانونية",
        label_en="Legal Service Request",
        page=service_request_page,
        order=1
    )

    upsert_link(
        column=cols["customers"],
        label_ar="الأسئلة الشائعة",
        label_en="FAQ",
        page=faq_page,
        order=2
    )

    upsert_link(
        column=cols["customers"],
        label_ar="طرق التواصل",
        label_en="Contact Methods",
        page=contact_methods_page,
        order=3
    )

    # ================= ETHICS =================
    charter_page = Page.objects.get(slug="professional-charter")
    conduct_page = Page.objects.get(slug="code-of-conduct")
    confidentiality_page = Page.objects.get(slug="confidentiality-rules")

    upsert_link(
        column=cols["ethics"],
        label_ar="ميثاق الامتثال المهني",
        label_en="Professional Charter",
        page=charter_page,
        order=0
    )

    upsert_link(
        column=cols["ethics"],
        label_ar="نظام السلوك المهني",
        label_en="Code of Conduct",
        page=conduct_page,
        order=1
    )

    upsert_link(
        column=cols["ethics"],
        label_ar="قواعد سرية المعلومات",
        label_en="Confidentiality",
        page=confidentiality_page,
        order=2
    )

    # ================= LEGAL =================
    policies_root = upsert_link(
        column=cols["legal"],
        label_ar="السياسات",
        label_en="Policies",
        order=1
    )

    terms_page = Page.objects.get(slug="terms")
    info_conf_page = Page.objects.get(slug="info-confidentiality")
    data_disclaimer_page = Page.objects.get(slug="data-consent-disclaimer")
    cookies_page = Page.objects.get(slug="cookies-policy")
    service_policy_page = Page.objects.get(slug="service-advisory")

    upsert_link(
        column=cols["legal"],
        label_ar="الشروط والأحكام",
        label_en="Terms",
        page=terms_page,
        order=0
    )

    upsert_link(
        column=cols["legal"],
        parent=policies_root,
        label_ar="سياسة سرية المعلومات",
        label_en="Info Confidentiality",
        page=info_conf_page,
        order=0
    )

    upsert_link(
        column=cols["legal"],
        parent=policies_root,
        label_ar="إخلاء المسؤولية عن موافقة خصوصية البيانات",
        label_en="Data Consent Disclaimer",
        page=data_disclaimer_page,
        order=1
    )

    upsert_link(
        column=cols["legal"],
        parent=policies_root,
        label_ar="سياسة ملفات تعريف الارتباط",
        label_en="Cookies Policy",
        page=cookies_page,
        order=2
    )

    upsert_link(
        column=cols["legal"],
        parent=policies_root,
        label_ar="سياسة تقديم الاستشارات الخدمات",
        label_en="Service Advisory",
        page=service_policy_page,
        order=3
    )

    # ================= FINAL =================
    SystemSeed.objects.create(key="default_footer_v2")
