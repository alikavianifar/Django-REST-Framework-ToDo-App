from rest_framework import serializers

from accounts.models import Profile
from todo.models import Task


class TaskSerializer(serializers.ModelSerializer):
    snippet = serializers.ReadOnlyField(source="get_snippet")
    relative_url = serializers.URLField(source="get_absolute_api_url", read_only=True)
    absolute_url = serializers.SerializerMethodField(method_name="get_abs_url")

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "snippet",
            "priority",
            "relative_url",
            "absolute_url",
            "due_date",
            "completed",
        ]
        read_only_fields = ["id"]

    def get_abs_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.get_absolute_api_url())

    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)
        parser_context = getattr(request, "parser_context", None) or {}
        kwargs = parser_context.get("kwargs") or {}
        if kwargs.get("pk"):
            rep.pop("relative_url", None)
            rep.pop("absolute_url", None)
            rep.pop("snippet", None)
            rep["state"] = "Single"
        else:
            rep.pop("description", None)
            rep["state"] = "List"
        return rep

    def create(self, validated_data):
        validated_data["author"] = Profile.objects.get(
            user_id=self.context["request"].user.id
        )
        return super().create(validated_data)
