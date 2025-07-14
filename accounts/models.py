# Import libraries
from django.db import models
from django.contrib.auth.models import User

# Define models UserImages and Attendance
class UserImages(models.Model):
    # User type choices constants
    ADMINISTRATIVE = "administrative"
    STUDENT = "student"
    USER_TYPE_CHOICES = [
        (ADMINISTRATIVE, "Administrative"),
        (STUDENT, "Student"),
    ]
    # Model fields
    user_type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES, default=STUDENT)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    identification_number = models.CharField(max_length=15, unique=True)
    face_image = models.BinaryField()
    face_encoding = models.BinaryField(null=True, blank=True)

    def __str__(self):
        # Return the username as string representation
        return self.user.username

class Attendance(models.Model):
    # Attendance type choices constants
    ENTRY = "entry"
    EXIT = "exit"
    ATTENDANCE_TYPE_CHOICES = [
        (ENTRY, "Entry"),
        (EXIT, "Exit"),
    ]
    # Model fields
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    attendance_type = models.CharField(max_length=7, choices=ATTENDANCE_TYPE_CHOICES)

    def __str__(self):
        # Return  a string representation username, attendance type and timestamp
        return f"{self.user.username} - {self.attendance_type} at {self.timestamp}"