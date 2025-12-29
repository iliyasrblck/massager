from django.db import models
from django.contrib.auth.models import AbstractUser
from django_resized import ResizedImageField
# Create your models here.

#تابع های اور راد شده
def uplod_img(instance, filename):
    # instance = شیء کاربر
    # filename = نام فایل اصلی آپلود شده
    return f'profile/{instance.username}/{filename}'

def message_img(instance, filename):
    return f'messages/{instance.sender}/{filename}'



class User(AbstractUser):
    photo_profile = ResizedImageField(size=(300,300), crop=['middle', 'center'], quality=70, upload_to=uplod_img, blank=True, null=True, verbose_name="عکس پروفایل")
    bio = models.TextField(blank=True, null=True, verbose_name="بیوگرافی")
    phone_number = models.CharField(blank=True, null=True,max_length=11, verbose_name="شماره همراه")
    birth_date = models.DateField(blank=True, null=True, verbose_name="تاریخ تولد")

    def save(self, *args, **kwargs):
        try:
            old = User.objects.get(pk=self.pk)
        except User.DoesNotExist:
            old = None

        if old and old.photo_profile != self.photo_profile:
            old.photo_profile.delete(save=False)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.photo_profile:
            self.photo_profile.delete(save=False)
        super().delete(*args, **kwargs)


class Chat(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user1",verbose_name="یوزر یک")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user2",verbose_name="یوزر دو")
    create_chat = models.DateTimeField(auto_now_add=True, verbose_name="زمان ساخت چت")
    update_chat = models.DateTimeField(auto_now=True, verbose_name="اخرین پیام")
    user1_blocked_user2 = models.BooleanField(default=False)
    user2_blocked_user1 = models.BooleanField(default=False)

    class Meta:
        verbose_name = "چت"
        verbose_name_plural = "چت ها"
        unique_together = ("user1", "user2")

    def __str__(self):
        return f"{self.user1} , {self.user2}"


class Massage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE,related_name='massage')
    sender = models.ForeignKey(User, on_delete=models.CASCADE,related_name='massage')
    text = models.TextField(blank=True, null=True)
    pic = ResizedImageField(blank=True, null=True, upload_to=message_img, )
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "پیام"
        verbose_name_plural = "پیام ها"
        ordering = ['create_at']

    def __str__(self):
        return f"{self.sender} : {self.text}"


