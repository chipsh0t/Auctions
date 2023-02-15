from django import forms
from .models import Auction, Comment, Bid,Category

#Create your forms here

#form for auction model
class AuctionForm(forms.ModelForm):
  class Meta:
    model = Auction
    exclude = ['creator','winner','auction_bids', 'auction_comments']
    #styling form fields with bootstrap
    widgets={
      'title': forms.TextInput(attrs={'class':'form-control'}),
      'starting_bid': forms.NumberInput(attrs={'class':'form-control'}),
      'photo':forms.URLInput(attrs={'class':'form-control'}),
      'category':forms.Select(attrs={'class':'form-control form-select'}),
      'description':forms.Textarea(attrs={'class':'form-control'}),
    }
  
  #overloading init to get rid of the empty category field
  def __init__(self, *args, **kwargs):
    super(AuctionForm,self).__init__(*args,**kwargs)
    self.fields['category'].empty_label=None

#form for comment model
class CommentForm(forms.ModelForm):
  class Meta:
    model = Comment
    exclude=['author', 'auction']
    #styling form fields with bootstrap
    widgets={
      'text':forms.TextInput(attrs={'class':'form-control'})
    }

#forms for bids
class BidForm(forms.ModelForm):
  class Meta:
    model = Bid
    exclude = ['bidder', 'auction']
    #styling form fields with bootstrap
    widgets={
      'bid':forms.NumberInput(attrs={'class':'form-control'})
    }