from django.db import models  # type: ignore

class Resume(models.Model):
    user_name = models.CharField(max_length=100)
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_name