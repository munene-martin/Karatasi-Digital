from django.db import models
from django.contrib.auth.models import User # <--- 1. Check this import

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) # <--- 2. Check this line
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='scans/')
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    is_paid = models.BooleanField(default=False)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_receipt = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title