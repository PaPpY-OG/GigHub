from django.urls import path
from . import views
urlpatterns = [
    path('freelancer/signup/',views.freelancerSignup, name='freelancersignupPage'),
    path('freelancer/login/',views.freelancerLogin,name='freelancerloginPage'),
    path('freelancer/dashboard/',views.freelancerDash, name='freelancer_dash'),
    path('freelancer/logout/',views.freelancerLogout, name='freelancer_logout'),
    path('freelancer/profile/',views.profile_page, name='Fprofile_page'),
    path('freelancer/profile/edit/',views.edit_profile, name='edit_Fprofile_page'),
    path('freelancer/activegigs/',views.active_gigs, name='active_gigs'),
    path('bid/<int:gig_id>/', views.submit_bid, name='submit_bid'),
    path('freelancer/bids/', views.my_bids, name='my_bids'),
    path('withdraw_bid/<int:bid_id>/', views.withdraw_bid, name='withdraw_bid'),
    path('freelancer/start_convo/<int:bid_id>/', views.start_convo, name='start_convo'),
    path('freelancer/messages/<int:convo_id>/', views.messages, name='messages'),
    path('freelancer/orders/', views.freelancerOrders, name='freelancer_orders')
]