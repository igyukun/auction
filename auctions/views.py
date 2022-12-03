from turtle import title
from unicodedata import category, decimal
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, models
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Max
import re

from .models import Category, Listing, User, Bid, Comment, WatchList, Winner
from .utils import DEBUG_PRINT

#   Render the initial page (index.html)
def index(request):
    err_message = None
    listings = Listing.objects.all()
    if len(listings) == 0:
        err_message = "No active listings found."
        
    return render(request, "auctions/index.html", {
        "title": "Active listings",
        "categories": Category.objects.all().order_by("name"),
        "listings":listings,
        "err_message": err_message
        })


#   Display the listings belonging to the selected category
#   Utilize the index.html template
def show_category_list (request, category_name):
    listings = Listing.objects.filter(category = Category.objects.get(name=category_name), is_active = True)
    return render(request, "auctions/index.html", {
        "title": f"{category_name.capitalize()}",
        "categories": Category.objects.all().order_by("name"),
        "listings": listings
    })


#   Renders a listing page from listing.html tempalte
def get_listing(request, listing_title):
    listing = Listing.objects.get(title=listing_title)  
    winner = Winner()
    
    #   If listing is inactive meaning the listing was closed 
    #   and the winner should be displayed in the template
    if not listing.is_active:
        winner = Winner.objects.get(listing=listing)
        
    return render (request, "auctions/listing.html", {
        "categories": Category.objects.all().order_by("name"),
        "listing" : listing,
        "bids_count": get_bids_count(listing_title),
        "last_bid_time": get_last_bid_time(listing_title),
        "last_bid_user": get_last_bid_user(listing_title),
        "comments": get_comments(listing_title),
        "is_watched": is_watched(listing_title, request.user),
        "winner": winner
    })

#   Add a new listing for authenticated user
#   or redirect to login screen using the decorator
@login_required(login_url='login')
def add_listing(request):
    err_message = None
    success_message = None
    new_listing = Listing()
    
    if request.method == "POST":
      
        #   Acquire and valudate the new listing paramters
        #   sent with the POST request
        try:
            new_listing.user = User.objects.get(pk = request.POST["user_id"])
            new_listing.title = request.POST["title"]
            new_listing.description = request.POST["description"]
            new_listing.starting_bid = request.POST["starting_bid"]
            new_listing.current_price = request.POST["starting_bid"]
            if new_listing.title == '':
                raise ValidationError("The listing Title cannot be empty")
            if new_listing.starting_bid == "" :
                raise ValidationError("Set the Starting Price.")
            # check if the request contains any uploaded file (a listing image)
            if len(request.FILES.keys()) == 0:
                new_listing.image = None
            else:
                new_listing.image = request.FILES["listing_image"]
            # check if the category exist
            try: 
                new_listing.category = Category.objects.get(name=request.POST["category"])
            except Category.DoesNotExist: 
                raise ValidationError("Select the Category.")
            
            new_listing.is_active = True
            new_listing.save()
            
        except (IntegrityError, ValidationError) as e:
            err_message = e.message
        else:
            success_message = f'The new item "{new_listing.title}" has been successfully added.'
            return HttpResponseRedirect(reverse("get_listing", args={new_listing.title}), {
                "success_message": success_message
                })  
    
    return render(request, "auctions/add_listing.html", {
        "listing": new_listing,
        "categories": Category.objects.all().order_by("name"),
        "err_message": err_message,
        "success_message": success_message
    })


#   Edit a listing data:
#   'title', 'description', 'category' fields can be altered
def edit_listing(request, listing_title):
    success_message = None
    err_message = None
    listing = Listing()

    try:
        listing = Listing.objects.get(title=listing_title)     
    except:
        return HttpResponseRedirect(reverse("get_listing", args={listing_title}), {
            "error_message": f"The listing {listing_title} could not be opened."
        })
    
    if request.method == "POST":
        #   Acquire and valudate the listing paramters
        #   sent with the POST request
        try:
            listing.user = User.objects.get(pk=request.POST["user_id"])
            listing.title = request.POST["title"]
            listing.description = request.POST["description"]
            if listing.title == '':
                raise ValidationError("The listing Title cannot be empty")
            try:
                listing.category = Category.objects.get(
                name=request.POST["category"])
            except Category.DoesNotExist:
                raise ValidationError("Select the Category.")
            
            listing.save(update_fields = ['title', 'description', 'category'])  
        except (IntegrityError, ValidationError) as e:
            err_message = e.message        
        else:
            success_message = f'The item "{listing.title}" has been updated successfully.'
            return HttpResponseRedirect(reverse("get_listing", args={listing.title}), {
                "success_message": success_message
            })
            
    return render(request, "auctions/edit_listing.html", {
        "categories": Category.objects.all().order_by("name"),
        "listing": listing,
        "err_message": err_message,
        "success_message": success_message
    })
    

#   Add listing to the Watchlist for authenticated user
#   or redirect to login screen using the decorator
@login_required(login_url='login')
def add_to_watch(request, listing_title):
    err_message = None
    if not is_watched(listing_title, request.user):
        try:
            watch = WatchList()
            watch.user = request.user
            watch.listing = Listing.objects.get(title=listing_title)
            watch.save()
        except:
            err_message = f"Could not add to watchlist"
    else:
        err_message = f"The listing is already watched by you." 
          
    return HttpResponseRedirect(reverse("get_listing", args={listing_title}), {
         "error_message": err_message
     })


#   Remove listing from the Watchlist for authenticated user
#   or redirect to login screen using the decorator
@login_required(login_url='login')
def remove_from_watch(request, listing_title):
    err_message = None
    if is_watched(listing_title, request.user):
        try:
            watch = WatchList.objects.filter(
                user=request.user, listing=Listing.objects.get(title=listing_title))
            watch.delete()
        except:
            err_message = f"Could not remove the listing from your watchlist."
    else:
        err_message = f"The listing is not in your watchlist."

    return HttpResponseRedirect(reverse("get_listing", args={listing_title}), {
        "error_message": err_message
    })


#   Display the Watchlist for authenticated user
#   or redirect to login screen using the decorator
@login_required(login_url='login')
def whatch_list(request):
    listings = []
    err_message = None
    
    for listing in Listing.objects.all():
        if is_watched(listing.title, request.user):
            listings.append(listing)
    if len(listings) == 0:
        err_message = f"The watch list is empty."
            
    return render(request, "auctions/index.html", {
        "title": f"Your Watch List ({len(listings)})",
        "categories": Category.objects.all().order_by("name"),
        "listings": listings,
        "err_message": err_message
    })
           

#   Display the winnings list to authenticated user
#   or redirect to login screen using the decorator
@login_required(login_url='login')
def wins_list(request):
    listings = []
    err_message = None
    
    for listing in Listing.objects.all():
        if not listing.is_active and is_winner(listing, request.user):
            listings.append(listing)
    if len(listings) == 0:
        err_message = f"No wins yet."
            
    return render(request, "auctions/index.html", {
        "title": f"Your Wins List ({len(listings)})",
        "categories": Category.objects.all().order_by("name"),
        "listings": listings,
        "err_message": err_message
    })
    
    
#   Check if the listing is being watched by a specified user
def is_watched(listing_title, user):
    if user.is_authenticated:
        try:
            listingObj = Listing.objects.get(title=listing_title)
            userObj = User.objects.get(pk=user.id)
            watchlist = WatchList.objects.filter(user = userObj, listing = listingObj)
            if watchlist.count() != 0:
                return True
            else:
                raise WatchList.DoesNotExist
        except WatchList.DoesNotExist:
            return False
    else:
        return False
    

#   Check if the listing was won by a specified user
def is_winner(listing, user):
    if user == Winner.objects.get(listing = listing).user:
        return True
    else:
        return False


#   Place a new bid and update the listing current price for an authenticated user
#   or redirect to login screen using the decorator
@login_required(login_url='login')
def place_bid(request, listing_title):
    success_message = None
    err_message = None
    
    try:
        listing = Listing.objects.get(title=listing_title)   
    except:
        return HttpResponseRedirect(reverse("get_listing", args={listing_title}), {
            "error_message": f"The listing {listing_title} could not be opened."
        })  
        
    if request.method == "POST":
        try:
            bid = Bid()
            bid.user = User.objects.get(pk=request.POST["user_id"])
            bid.listing = listing
            if float(request.POST["bid_price"]) <= listing.current_price:
                raise ValidationError(f"Your bid should be higher than {listing.current_price}")
            bid.bid_price = request.POST["bid_price"]
            bid.save()  
            
            listing.current_price = request.POST["bid_price"]
            listing.save(update_fields=['current_price'])
            
        except (IntegrityError, ValidationError) as e:
            err_message = e.message
        else:
            success_message = f'The bid has been placed successfully.'
            return HttpResponseRedirect(reverse("get_listing", args={listing_title}), {
                "success_message": success_message
            })
    
    return render(request, "auctions/place_bid.html", {
        "categories": Category.objects.all().order_by("name"),
        "listing": listing,
        "err_message": err_message,
        "success_message": success_message
    })


#   Add a comment to the listing and return to the same listing page
def add_comment(request):
    err_message = None
    if request.method == "POST":
        try:
            comment = Comment()
            comment.user = User.objects.get(pk = request.POST["user_id"])
            comment.listing = Listing.objects.get(title = request.POST["listing_title"])
            comment.text = request.POST["text"]
            comment.save()
        except IntegrityError as e:
                err_message = e.message
                
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


#   Close listing and update a winner model with the highest big user and price. 
#   Set the listing is_active to False to indicate that the listing is closed
def close_listing(request, listing_title):
    err_message = None
    winner_message = None
    bid = Bid()
    winner = Winner()
    
    listing = Listing.objects.get(title = listing_title)
    bid = get_highest_bid(listing)
    if bid == None:
        err_message = f"Closed without a winner since no bids have been put for this listing."
    else:
        winner = Winner()
        winner.user = bid.user
        winner.listing = bid.listing
        winner.price = listing.current_price
        try:
            winner.save()
            winner_message = f"User {winner.user} has won this lot with a bid of USD{winner.price}."
        except:
            err_message = "Could not update the winner."
            return HttpResponseRedirect(reverse("get_listing", args={listing_title}), {
                "error_message": err_message
            })
        listing.is_active = False
        
        try:
            listing.save(update_fields=['is_active'])
        except:
            err_message = "Could not close the listing."
            return HttpResponseRedirect(reverse("get_listing", args={listing_title}), {
                "error_message": err_message
            })
    
    
    return HttpResponseRedirect(reverse("get_listing", args={listing_title}), {
        "error_message": err_message,
        "winner_message": winner_message
    })


#   Return the number of bids for a specific listing title
def get_bids_count(listing_title):
    bids_count = Bid.objects.filter(listing=Listing.objects.get(
        title=listing_title)).count()
    return bids_count
  

#   Retun the timestamp of the most recent bid for a specific listing title
def get_last_bid_time(listing_title):
    bid_time = Bid.objects.filter(
        listing=Listing.objects.get(title=listing_title)).aggregate(Max('bid_place_date'))  
    return bid_time['bid_place_date__max']


#   Return the user that has put the most recent bid for a specific listing title
def get_last_bid_user(listing_title):
    try:
        bid = Bid.objects.get(
            listing=Listing.objects.get(title=listing_title), bid_place_date=get_last_bid_time(listing_title))
        return bid.user
    except Bid.DoesNotExist:
        return None


#   Return the highest bid for the specified listing from the Bid model
def get_highest_bid(listingObj):
    bid = Bid()
    try:    
        bid = Bid.objects.get(listing=listingObj, bid_price = listingObj.current_price)
    except:
        bid = None
    
    DEBUG_PRINT(f"The highest bid for {listingObj}: {bid}")
    
    return bid


#   Add a new category to the category list and load the current template
def add_category(request):  
    err_message = None
    if request.method == "POST":
        name = request.POST["name"]
        try:
            category = Category()
            category.name = name.strip().capitalize()
            category.save()
        except IntegrityError:
                err_message = f"Category '{name}' already exists."
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
   
    
#   Return the list of comments for a specific listing title
def get_comments(listing_title):
    return Comment.objects.filter(listing=Listing.objects.get(title=listing_title)).order_by('-creation_time')
 
 
#   Display log-in page and authenticate the user     
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "categories": Category.objects.all().order_by("name"),
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


#   Sign out the currently authenticated user
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


#   Register an new user
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        # if password != confirmation:
        message = validate_password(password, confirmation)
        if message != None:
            return render(request, "auctions/register.html", {
                "categories": Category.objects.all().order_by("name"),
                "message": message
            })

        # Attempt to create new user
        try:
            try:
                user = User.objects.create_user(username, email, password)
                user.first_name = first_name
                user.last_name = last_name
            except ValueError:
                return render(request, "auctions/register.html", {
                    "categories": Category.objects.all().order_by("name"),
                    "message": "Please provide a valid username."
                })
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "categories": Category.objects.all().order_by("name"),
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


#   Validate the password lenght and matching the confirmation
def validate_password(password, confirmation):
    if password != confirmation:
        return "Passwords must match."
    
    if len(password) < 6:
        return "Password must be at least 6 characters long."
    
    return None

#   Validate email address pattern
def validate_email(email):

    # Make a regular expression for validating an Email
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    if email and re.fullmatch(regex, email):
        return True
