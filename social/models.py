from django.conf import settings
from django.db import models
from django.db.models import F, Q


class FriendRequest(models.Model):
    """A pending request, or, once accepted, the friendship itself.

    Declining, cancelling and unfriending delete the row, so either person can send a fresh request later.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING"
        ACCEPTED = "ACCEPTED"

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_friend_requests")
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_friend_requests")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["from_user", "to_user"], name="unique_friend_request_direction"),
            models.CheckConstraint(condition=~Q(from_user=F("to_user")), name="no_self_friend_request"),
        ]
