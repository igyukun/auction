from enum import unique
from wsgiref.validate import validator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxLengthValidator


class User(AbstractUser):
    image = models.ImageField(
        upload_to="images/users/", null=True, blank=True)
     

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
        
    def __str__(self):
        return f"{self.name}"   


class Listing(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listing_user", null=False)
    title = models.CharField( max_length=100, unique=True, blank=False)
    description = models.TextField(max_length = 1024, blank = True, null = True, validators=[MaxLengthValidator(1024)])
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creation_time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="images/%Y/%m/%d/", null=True, blank=True, unique = False)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="categories")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"listing: {self.title}, created by {self.user}"



class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid_users")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bid_listings")
    bid_price = models.DecimalField(max_digits=10, decimal_places=2)
    bid_place_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bid for the listing {self.listing}. The current bid is {self.bid_price}. Placed on {self.bid_place_date}."
    

class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comment_users")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comment_listings")
    text = models.CharField(max_length=2048)
    creation_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment for the {self.listing}: "{self.text}" Added by {self.user} on {self.creation_time}.'
    
    
class WatchList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="watchlist_users")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="watchlist_listings")

    def __str__(self):
        return f"{self.user} is whatching {self.listing}"
    

class Winner(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="winner_users")
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="winner_listings")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user} won {self.listing} for USD{self.price}"
