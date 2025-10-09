from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from Client.models import Profile, Order, Bid, Gig, Conversation, Message
from django.http import HttpResponseForbidden
from django.db.models import Q

# Create your views here.

def freelancerSignup(request: HttpRequest):
    error = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password1= request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2 or len(password1) < 8 :
            error = "passwords must match and must not be less than 8"
        else :
            try :
                user_exist= User.objects.filter(username=email).first()
                if user_exist :
                    error = 'User already exists for this account'
                else :
                    user = User.objects.create_user(username=email, password=password1)
                    user.save()
                    return redirect('freelancerloginPage')
            except Exception as e:
                error = str (e)
    return render(request, 'signup4.html', {'error':error})

def freelancerLogin(request: HttpRequest):
    error,message= None, None
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        if not password or len(password) < 8 :
            return render(request, 'login4.html', {"error":True, "message":"password is required and must meet minimun length to login"})
        user_auth = authenticate(request, username=email, password=password)
        if not user_auth :
            return render(request, 'login4.html',{"error":True, "message":"Invalid Credentials"})
        login(request, user_auth,)
        return redirect("freelancer_dash")
    return render(request, 'login4.html', {"error":error,"message":message})

@login_required(login_url='freelancerloginPage')
def freelancerDash(request: HttpRequest):
    total_orders = Order.objects.filter(freelancer=request.user).count()
    return render(request, 'dashboard.html', { 'total_orders': total_orders})

@login_required(login_url='freelancerloginPage')
def profile_page(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Check if profile is complete
    is_complete = all([
        profile.role,
        profile.bio.strip() if profile.bio else False,
        profile.photo
    ])

    # Handle form submission
    if request.method == 'POST':
        profile.role = request.POST.get('role')
        profile.bio = request.POST.get('bio')
        if request.FILES.get('photo'):
            profile.photo = request.FILES['photo']
        profile.save()
        return redirect('Fprofile_page')  # Redirect to refresh the page

    return render(request, 'Fprofile.html', {
        'profile': profile,
        'is_complete': is_complete
    })

@login_required(login_url='freelancerloginPage')
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        profile.role = request.POST.get('role')
        profile.bio = request.POST.get('bio')
        if request.FILES.get('photo'):
            profile.photo = request.FILES['photo']
        profile.save()
        return redirect('Fprofile_page')  # or wherever you want to go after saving

    return render(request, 'Fprofile.html', {'profile': profile})

@login_required(login_url='freelancerloginPage')
def active_gigs(request: HttpRequest):
    gigs = Gig.objects.filter(status='OPEN').order_by('-created_at')
    return render(request, 'activegigs.html', {'gigs': gigs})

@login_required(login_url='freelancerloginPage')
def submit_bid(request: HttpRequest, gig_id):
    gig = get_object_or_404(Gig, id=gig_id)
    
    error, success = None, None
    if request.method == "POST":
        amount = request.POST.get('amount')
        days = request.POST.get('days')
        cover_letter = request.POST.get('cover_letter')
        mybids = request.session.get('mybids', [])
        
        if not amount or not days or not cover_letter:
            error = "All fields are required."
            return render(request, 'submit_bid.html', {"error": error, "gig": gig})
        
        if Bid.objects.filter(gig=gig, freelancer=request.user, status='PENDING').exists():
            error = 'You have already placed a bid on this gig.'
            return render(request, 'submit_bid.html', {"error": error, "gig": gig})
        else:
            Bid.objects.create(freelancer=request.user, gig=gig, amount=amount, days=days, cover_letter=cover_letter)
            mybids.append(gig_id)
            request.session['mybids'] = mybids
            gigs = Gig.objects.filter(status = "OPEN").order_by('-created_at')
            success = 'Bid submitted successfully'
            return render(request, 'activegigs.html', {"gigs":gigs, "success":success})
    return render(request, 'submit_bid.html', {"gig": gig, "error": error, "success": success})

@login_required(login_url='freelancerloginPage')
def my_bids(request: HttpRequest):
    bids = Bid.objects.filter(freelancer=request.user).order_by('-created_at')
    return render(request, 'mybids.html', {'bids': bids})

@login_required(login_url='freelancerloginPage')
def edit_bid(request, bid_id):
    bid = get_object_or_404(Bid, id = bid_id, freelancer=request.user)

    if request.method == 'POST':
        bid.amount = request.POST.get('amount')
        bid.days = request.POST.get('days')
        bid.cover_letter = request.POST.get('cover_letter')
        bid.save()
        return redirect('my_bids')
    return render(request, 'edit_bid.html', {'bid':bid})

@login_required(login_url='freelancerloginPage')
def withdraw_bid(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id, freelancer=request.user)
    bid.delete()
    # Also remove from session if present
    mybids = request.session.get('mybids', [])
    if bid.gig.id in mybids:
        mybids.remove(bid.gig.id)
        request.session['mybids'] = mybids
    return redirect('my_bids')

@login_required(login_url='freelancerloginPage')
def freelancerOrders(request):
    orders = Order.objects.filter(freelancer=request.user).select_related('gig', 'bid')
    return render(request, 'orders.html', {'orders': orders})

@login_required(login_url='freelancerloginPage')
def start_convo(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id)
    convo, created = Conversation.objects.get_or_create(client = bid.gig.client, freelancer = bid.freelancer)
    return redirect('conversations', convo.id)

@login_required(login_url='freelancerloginPage')
def conversations(request, convo_id):
    convo = get_object_or_404(Conversation, id=convo_id)
    
    if request.user not in [convo.client, convo.freelancer]:
        return HttpResponseForbidden()

    if request.method == 'POST':
        Message.objects.create(conversation=convo,sender=request.user,text=request.POST['text'])
        return redirect('conversations', convo.id)

    messages = convo.message_set.order_by('sent_at')
    return render(request, 'conversations.html', {'convo': convo, 'messages': messages})

@login_required(login_url='freelancerloginPage')
def message_view(request):
    conversations = Conversation.objects.filter(Q(client=request.user) | Q(freelancer=request.user)).order_by('-updated_at')
    return render(request, 'message.html', {'conversations': conversations})

@login_required(login_url='freelancerloginPage')
def freelancerLogout(request: HttpRequest):
    logout(request)
    return render (request, 'login4.html')