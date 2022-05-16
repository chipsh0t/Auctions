from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name = "new_listing"),
    path("listing/<int:id>", views.listing_page, name = "listing_page"),
    path("watchlist", views.watchlist_page, name = "watchlist"),
    path("category/<str:name>", views.single_category_page, name="single_category")
]
