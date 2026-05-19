from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("applications.users.urls")),
    path("api/", include("applications.quizzes.urls")),
    path("api/", include("applications.histories.urls")),
    path("api/", include("applications.rooms.urls")),
]
