from django.contrib import admin

from .models import Choice, Question, Quiz


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "owner__username")


admin.site.register(Question)
admin.site.register(Choice)
