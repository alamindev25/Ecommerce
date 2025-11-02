from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class GlobalReport(models.Model):
    REPORT_TYPES = (
        ('complain', 'Complain'),
        ('suggestion', 'Suggestion'),
        ('feedback', 'Feedback'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='global_reports')
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    report_content = models.TextField()
    report_image = models.ImageField(upload_to='global_reports_image/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user_id.phone} - {self.report_type} - {self.status}" 