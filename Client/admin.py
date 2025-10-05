from django.contrib import admin
from . models import Profile, Gig,Bid,Order, Attachment, Conversation, Message, Review
# Register your models here.
admin.site.register(Profile)
admin.site.register(Gig)
admin.site.register(Bid)
admin.site.register(Order)
admin.site.register(Attachment)
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Review)
