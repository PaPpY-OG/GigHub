from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpRequest
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Gig, Bid, Profile, Order, Conversation, Message
from django.http import HttpResponseForbidden
from django.db.models import Q

# Create your views here.
def landingpage(request: HttpRequest):
    return render(request, 'landpage.html')

def clientSignup(request: HttpRequest):
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
                    return redirect('clientloginPage')
            except Exception as e:
                error = str (e)
    return render(request, 'signup3.html', {'error':error})

def clientLogin(request: HttpRequest):
    error,message= None, None
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        if not password or len(password) < 8 :
            return render(request, 'login3.html', {"error":True, "message":"password is required and must meet minimun length to login"})
        user_auth = authenticate(request, username=email, password=password)
        if not user_auth :
            return render(request, 'login3.html',{"error":True, "message":"Invalid Credentials"})
        login(request, user_auth,)
        return redirect("client_dash")
    return render(request, 'login3.html', {"error":error,"message":message})

@login_required(login_url='clientloginPage')
def clientDash(request):
    gigs = Gig.objects.filter(client=request.user).order_by('-created_at')
    total_gigs = Gig.objects.filter(client=request.user).count()
    recent_bids = Bid.objects.filter(gig__client=request.user).order_by('-created_at')[:5]
    return render(request, 'clientdash.html', { 'total_gigs': total_gigs, 'recent_bids': recent_bids, "gig":gigs})

@login_required(login_url='clientloginPage')
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
        return redirect('profile_page')  # Redirect to refresh the page

    return render(request, 'profile.html', {
        'profile': profile,
        'is_complete': is_complete
    })

@login_required(login_url='clientloginPage')
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        profile.role = request.POST.get('role')
        profile.bio = request.POST.get('bio')
        if request.FILES.get('photo'):
            profile.photo = request.FILES['photo']
        profile.save()
        return redirect('profile_page')  # or wherever you want to go after saving

    return render(request, 'profile.html', {'profile': profile})

@login_required(login_url='clientloginPage')
def createGig(request : HttpRequest):
    error, message = None, None
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        budgetmin = request.POST.get('budget_min')
        budgetmax = request.POST.get('budget_max')
        description = request.POST.get('description')
        status = 'OPEN'
        client = request.user
        #first check if gig already existed
        try:
            gig_exist = Gig.objects.filter(title=title).first()
            if gig_exist :
                error = 'Gig already exist for this title'
            else :
                budgetmin = float(budgetmin)
                budgetmax = float(budgetmax)
                client = request.user
                gigs = Gig.objects.create(title=title, category=category, budget_min=budgetmin, budget_max=budgetmax, 
                description=description, status=status, client=client)
                gigs.save()
                message="Gig created successfully"
                return redirect('client_dash')
        except Exception as e :
            error = str (e)
    return render(request, 'creategig.html', {"error":error, "message":message})

@login_required(login_url='clientloginPage')
def viewGig(request: HttpRequest):
    gigs = Gig.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'viewgig.html', {'gigs': gigs})

@login_required(login_url='clientloginPage')
def view_bids_for_gig(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id, client=request.user)
    bids = Bid.objects.filter(gig=gig).select_related('freelancer').order_by('-created_at')
    return render(request, 'viewbids.html', {'gig': gig,'bids': bids})

@login_required(login_url='clientloginPage')
def accept_bid(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id, gig__client=request.user)
    # Prevent accepting if gig is already assigned
    if bid.gig.status != 'OPEN':
        error = "This gig has already been assigned to another freelancer."
        return redirect('view_bids_for_gig', gig_id=bid.gig.id)
    bid.status = 'ACCEPTED'
    bid.save()

    Bid.objects.filter(gig=bid.gig).exclude(id=bid.id).update(status='REJECTED')

    bid.gig.status = 'ASSIGNED'
    bid.gig.save()
    if not Order.objects.filter(gig=bid.gig).exists():
        Order.objects.create(gig=bid.gig, freelancer=bid.freelancer,agreed_amount=bid.amount,milestones=[],status='IN_PROGRESS')
    return redirect('view_bids_for_gig', gig_id=bid.gig.id)

def reject_bid(request, bid_id):    
    bid = get_object_or_404(Bid, id=bid_id, gig__client=request.user)
    bid.status = 'REJECTED'
    bid.save()
    return redirect('view_bids_for_gig', gig_id=bid.gig.id)

@login_required(login_url='clientloginPage')
def delete_gig(request, gig_id):
    gig = get_object_or_404(Gig, id=gig_id, client=request.user)
    gig.delete()
    return redirect('viewGig')

@login_required(login_url='clientloginPage')
def start_conversation(request, bid_id):
    bid = get_object_or_404(Bid, id=bid_id)
    convo, created = Conversation.objects.get_or_create(client = bid.gig.client, freelancer = bid.freelancer)
    return redirect('conversation', convo.id)

@login_required(login_url='clientloginPage')
def conversation(request, convo_id):
    convo = get_object_or_404(Conversation, id=convo_id)
    
    if request.user not in [convo.client, convo.freelancer]:
        return HttpResponseForbidden()

    if request.method == 'POST':
        Message.objects.create(conversation=convo,sender=request.user,text=request.POST['text'])
        return redirect('conversation', convo.id)

    messages = convo.message_set.order_by('sent_at')
    return render(request, 'conversation.html', {'convo': convo, 'messages': messages})

@login_required(login_url='clientloginPage')
def inbox_view(request):
    conversations = Conversation.objects.filter(Q(client=request.user) | Q(freelancer=request.user)).order_by('-updated_at')
    return render(request, 'inbox.html', {'conversations': conversations})

@login_required(login_url='clientloginPage')
def clientlogout(request: HttpRequest):
    logout(request)
    return render (request, 'login3.html')
