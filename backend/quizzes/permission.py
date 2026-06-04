from rest_framework.permissions import BasePermission
from .models import Quiz

class IsQuizOwner(BasePermission):
    message = "Only quiz owner can do it"

    def has_object_permission(self, request, view, quiz: Quiz):
        return quiz.owner_id == request.user.id
        