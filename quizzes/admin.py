
"""Configure the Django admin interface for quizzes and questions."""

from django.contrib import admin

from quizzes.models import Question, Quiz


class QuestionInline(admin.TabularInline):
    """Allow questions to be managed directly inside a quiz."""

    model = Question
    extra = 0


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Configure the admin interface for quizzes."""

    list_display = (
        "title",
        "user",
        "video_url",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("title", "description", "user__username")
    readonly_fields = ("created_at", "updated_at")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Configure the admin interface for individual questions."""

    list_display = (
        "question_title",
        "quiz",
        "created_at",
        "updated_at",
    )
    search_fields = ("question_title", "quiz__title")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
