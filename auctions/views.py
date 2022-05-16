from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import AuctionForm, CommentForm, BidForm
from .models import User, Auction, Comment, Bid, Category


def index(request):
    all_listings = Auction.objects.filter(winner = None)
    return render(request, "auctions/index.html", {
        "listings" : all_listings
    })


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
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

#this function lets user to create a new listing
def create_listing(request):
    if request.method == "POST":
        #if user sends request to save a new auction
        form = AuctionForm(request.POST)
        if form.is_valid():
            #if user input is valid, open index page with a new listing added to it
            #adding info about the creator of the auction
            saved_auction = form.save(commit = False)
            saved_auction.creator = request.user
            saved_auction.starting_bid = abs(float(request.POST['starting_bid']))
            saved_auction.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            #if input is invalid stay on the same page
            return render(request, "auctions/create_listing.html", {
                "form" : form
            })
    else:
        #user is redirected to an empty auction form if Create Listing button is clicked
        return render(request, "auctions/create_listing.html", {
            "form" : AuctionForm()
        })

#this function is called when user wants to add a comment
def add_comment(request, id, comments, bids):
    #if user wants to comment we edit their input to fit out DB models
    listing = Auction.objects.get(pk = id)
    comment_form = CommentForm(request.POST)
    if comment_form.is_valid():
        #adding data for all Comment fields
        new_comment = comment_form.save(commit = False)                
        new_comment.author = request.user
        new_comment.auction = listing
        new_comment.save()
        return HttpResponseRedirect(reverse("listing_page", kwargs = {'id':listing.id}))
    else:
        return render(request, "auctions/listing_page.html",{
            "listing" : listing,
            "comments" : comments,
            "winning_bid" : bids[-1],
            "comments_form" : CommentForm(),
            "bids_form" : BidForm()
        })

#this function is called when a user wants to place a bid
def place_bid(request, id, comments, bids):
    listing = Auction.objects.get(pk = id)
    #collecting data from user input
    bid_form = BidForm(request.POST)
    if bid_form.is_valid():
        #getting the value of new bid money
        new_bid_money = float(request.POST["bid"])
        #whan a user enters a listing page, starting bid will be shown as the highest one
        if new_bid_money > bids[-1].bid:
            #if a new bid is more than current highest one, we should save it
            new_bid = bid_form.save(commit = False)
            new_bid.bidder = request.user
            new_bid.auction = listing
            new_bid.save()
            return HttpResponseRedirect(reverse("listing_page", kwargs = {'id':listing.id}))
        else:
            #if new bid is lower or equal to the current highest one, we show the error message
            return render(request, "auctions/listing_page.html", {
                "listing" : listing,
                "comments" : comments,
                "winning_bid" : bids[-1],
                "comments_form" : CommentForm(),
                "bids_form" : BidForm(),
                "message" : "Your bid should be higher than current price !"
            })
    else:
        #if form is not valid we render the page
        return render(request, "auctions/listing_page.html",{
            "listing" : listing,
            "comments" : comments,
            "winning_bid" : bids[-1],
            "comments_form" : CommentForm(),
            "bids_form" : BidForm()
        })


def close_listing(request,listing,winning_bid):
    #first we check if anyone had placed a bid on this auction before closing
    if request.user != winning_bid.bidder:
        #close the listing, notify the winner
        listing.winner = winning_bid.bidder
    else:
        #if nobody bid on the listing an item stays with the auction creator
        listing.winner = request.user
    listing.save()
    return render(request, "auctions/listing_page.html", {
        "listing" : listing
    })


#this function takes user to a listing page
def listing_page(request, id):
    if request.user.is_authenticated:
        # if user is logged in we should collect required data from the DB 
        #to render the requested listing page
        listing = Auction.objects.get(pk = id)
        #comments on the listing
        comments = [comment for comment in Comment.objects.filter(auction=listing.id)]
        #if it is empty the first one should be a starting price
        if len(list(Bid.objects.filter(auction=listing.id))) == 0:
            starting_price = BidForm()
            starting_price_edit = starting_price.save(commit = False)
            starting_price_edit.bid = listing.starting_bid
            starting_price_edit.bidder = listing.creator
            starting_price_edit.auction = listing
            starting_price_edit.save()
        #getting bids for the auction
        bids = [bid for bid in Bid.objects.filter(auction=listing.id)]
        #checking if user wants to interact
        if request.method == "POST":
            if request.POST.get("comment"):
                #if user wants to comment we call this function
                return add_comment(request, id, comments, bids)
            elif request.POST.get("bid"):
                #creator should not be able to increase price after staiting the starting price
                if request.user == listing.creator:
                    return HttpResponseRedirect(reverse("listing_page", kwargs = {'id':listing.id}))
                #if user wants to bid we call this function
                return place_bid(request, id, comments, bids) 
            elif request.POST.get("close"):
                #if creator wants to close the listing we call this function
                return close_listing(request,listing,bids[-1])
            elif request.POST.get("add_watchlist"):
                # if user wants to add an item to a watchlist
                request.user.watchlist.add(Auction.objects.get(pk=listing.id))
                return HttpResponseRedirect(reverse("listing_page", kwargs = {'id':listing.id}))
            elif request.POST.get("remove_watchlist"):
                # if user wants to remove an item from a watchlist
                request.user.watchlist.remove(listing)
                return HttpResponseRedirect(reverse("listing_page", kwargs = {'id':listing.id}))
        #render this just to redirect user on the listing page
        else:
            return render(request, "auctions/listing_page.html",{
                "listing" : listing,
                "comments" : comments,
                "winning_bid" : bids[-1],
                "comments_form" : CommentForm(),
                "bids_form" : BidForm()
            })
    else:
        #if user is not authenticated, don`t let them view a listing page
        return HttpResponseRedirect(reverse("index"))


#this function takes user to their watchlist page
def watchlist_page(request):
    watchlist_listings = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html",{
        "listings" : watchlist_listings
    })

#single category page
def single_category_page(request, name):
    return render(request, "auctions/category.html",{
        "listings" : Auction.objects.filter(category__category_name = name, winner=None)   
    })


