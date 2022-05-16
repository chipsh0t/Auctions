from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField('Auction', blank = 'True', related_name = "watchlist")

#table for bids
class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    bid = models.IntegerField()
    auction = models.ForeignKey('Auction', on_delete=models.CASCADE, related_name="bidded_on")
    
    def __str__(self):
        return "Bidder: " + str(self.bidder) + "; Bid: " + str(self.bid)

#table for comments
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    text = models.CharField(max_length=100)
    auction = models.ForeignKey('Auction', on_delete=models.CASCADE, related_name="comment_location")

    def __str__(self):
        return str(self.author) + " commented: " + str(self.text)

#table for auctions
class Auction(models.Model):
    creator = models.ForeignKey(User, null=True ,on_delete=models.CASCADE, related_name="creator")
    winner = models.ForeignKey(User, null = True, blank = 'True' ,on_delete=models.CASCADE, related_name="winner")
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_bid = models.IntegerField()
    photo = models.URLField(max_length = 500)
    category = models.ForeignKey('Category', blank = "False", on_delete=models.DO_NOTHING,related_name = "categories")
    #manyToMany fields
    auction_bids = models.ManyToManyField(Bid, blank = 'True', related_name= 'placed_bid')
    auction_comments = models.ManyToManyField(Comment, blank = 'True', related_name = "comments")

    def __str__(self):
        return "Auction for: " + str(self.title)

#table for categories
class Category(models.Model):
    category_name = models.CharField(max_length = 100)

    def __str__(self):
        return self.category_name