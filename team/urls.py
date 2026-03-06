# team/urls.py
from django.urls import path
from .views import PublicTeamView, TeamListCreateView, TeamDetailView, PublicTeamPageView, TeamPageAdminView

urlpatterns = [
    path("public/", PublicTeamView.as_view()),
    path("public/page/", PublicTeamPageView.as_view()),

    # Admin
    path("admin/members/", TeamListCreateView.as_view()),
    path("admin/members/<int:pk>/", TeamDetailView.as_view()),
    path("admin/page/", TeamPageAdminView.as_view()),

]
