from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", 
         views.index, name="index"),
    path("login", 
         views.login_view, name="login"),
    path("logout", 
         views.logout_view, name="logout"),
    path("register", 
         views.register, name="register"),
    path("add_category", 
         views.add_category, name="add_category"),
    path("watch_list", 
         views.whatch_list, name="watch_list"),
    path("wins_list", 
         views.wins_list, name="wins_list"),
    path("listing-<str:listing_title>", 
         views.get_listing, name="get_listing"),
    path("add_listing", 
         views.add_listing, name="add_listing"),
    path("edit_listing-<str:listing_title>",
         views.edit_listing, name="edit_listing"),
    path("close_listing-<str:listing_title>",
         views.close_listing, name="close_listing"),
    path("place_bid-<str:listing_title>", 
         views.place_bid, name="place_bid"),
    path("show_category_list-<str:category_name>",
         views.show_category_list, name="show_category_list"),
    path("add_comment", 
         views.add_comment, name="add_comment"),
    path("add_to_watch-<str:listing_title>",
         views.add_to_watch, name="add_to_watch"),
    path("is_watched-<str:listing_title>",
         views.is_watched, name="is_watched"),
    path("remove_from_watch-<str:listing_title>",
         views.remove_from_watch, name="remove_from_watch")
]

# add this lines
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
