from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class PersonalNotes(models.Model):
    # NOTE_TYPES = (
    #     ('admin_to_owner', 'Admin To Owner'),
    #     ('owner_to_admin', 'Owner To Admin'),
    #     ('owner_to_employee', 'Owner To Employee'),
    #     ('employee_to_owner', 'Employee To Owner'),
    #     ('own_to_own', 'Own To Own'),
    # )
    # sender_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_notes')
    # recipient_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notes')
    # note_type = models.CharField(max_length=50, choices=NOTE_TYPES)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_notes')
    note_title = models.CharField(max_length=150)
    note_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    def __str__(self):
        return f'{self.user_id} - {self.note_title}'
    
    class Meta:
        verbose_name_plural = 'Personal Notes'
        ordering = ['-created_at']