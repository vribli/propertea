from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    This class seeks to create a separate class to ensure the activation is needed for account usage.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    signup_confirmation = models.BooleanField(default=False)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    This method seeks to assist in the creation of new user profiles.

    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    This method seeks to assist in the saving of user profiles.

    """
    instance.profile.save()


class FavouriteProperty(models.Model):
    """
    This class seeks to save the User's favourite properties in a one-to-one relationship.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(max_length=100)
