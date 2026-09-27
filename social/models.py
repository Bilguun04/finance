from django.conf import settings
from django.db import models


class FriendRequest(models.Model):
	PENDING = "PENDING"
	ACCEPTED = "ACCEPTED"
	DECLINED = "DECLINED"
	STATUS_CHOICES = [(PENDING, "Pending"), (ACCEPTED, "Accepted"), (DECLINED, "Declined")]

	from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_friend_requests")
	to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_friend_requests")
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
	created_at = models.DateTimeField(auto_now_add=True)
	responded_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		constraints = [models.UniqueConstraint(fields=["from_user", "to_user"], name="unique_friend_request_direction")]

