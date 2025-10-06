from django.urls import path
from . import views

urlpatterns = [
    path('', views.landingpage, name='landPage' ),
    path('client/signup/', views.clientSignup, name='clientsignupPage'),
    path('client/login/',views.clientLogin, name='clientloginPage'),
    path('client/dash/', views.clientDash, name="client_dash"),
    path('creategig/',views.createGig, name="createGig"),
    path('viewgig/', views.viewGig, name="viewGig"),
    path('client/profile/', views.profile_page, name="profile_page"),
    path('client/edit/profile', views.edit_profile, name="edit_profile"),
    path('client/viewbid/<int:gig_id>/', views.view_bids_for_gig, name="view_bids_for_gig"),
    path('accept_bid/<int:bid_id>/', views.accept_bid, name="accept_bid"),
    path('reject_bid/<int:bid_id>/', views.reject_bid, name="reject_bid"),
    path('delete_gig/<int:gig_id>/', views.delete_gig, name="delete_gig"),
    path('start_conversation/<int:bid_id>/', views.start_conversation, name="start_conversation"),
    path('conversation/<int:convo_id>/', views.conversation, name="conversation"),
    path('client/inbox/', views.inbox_view, name="inbox_view"),
    path('client/logout/', views.clientlogout, name="client_logout")
]