from django.contrib import admin

from .models import *

# Register your models here.
class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "starting_bid", "creation_time", "category")


admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(WatchList)
admin.site.register(Winner)