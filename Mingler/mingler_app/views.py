
import random
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from itertools import chain

from .models import FollowerCount, LikePost, Profile, Post

# Create your views here.
@login_required(login_url='signin')
def index(request):
    
    if request.user.is_authenticated:
        
        try:
            
           #post feeds
            user_object = User.objects.get(username=request.user.username)
            user_profile = Profile.objects.get(user=user_object)

            user_following = FollowerCount.objects.filter(follower=request.user.username)

            user_following_list = []
            feed = []
            feed_list = []

            for users in user_following:
                user_following_list.append(users.user)

            for usernames in user_following:
                feed_lists = Post.objects.filter(user=usernames)
                feed.append(feed_lists)

            #Getting posts of following and user
            user_posts = Post.objects.filter(user=request.user.username)
            feed.append(user_posts)
            feed_list = list(chain(*feed))
    
            #user_suggestions
            all_users = User.objects.all()
            user_following_all = []
            new_users_suggestion = []

            for user in user_following:
                user_list = User.objects.get(username=user)
                user_following_all.append(user_list)

            current_user = User.objects.filter(username=request.user.username)
            for new_users in all_users:
                if new_users not in  user_following_all and new_users not in current_user:
                    new_users_suggestion.append(new_users)
                    random.shuffle(new_users_suggestion)

            username_profile = []
            username_profile_list = []

            for users in new_users_suggestion:
                 username_profile.append(users.id)
            
            for ids in username_profile:
                profile_list = Profile.objects.filter(id_user=ids)
                username_profile_list.append(profile_list)
            
            suggestion_list = list(chain(*username_profile_list))

            #Dynamic color for unlike and like button
            username = request.user.username
            
            
            
                
                

              
                    
            context = {
                'user_profile':user_profile,
                'posts':feed_list,
                'suggestion_list':suggestion_list[:4],
                
                
            }
            return render(request, 'index.html', context)

        except ObjectDoesNotExist:
            return HttpResponse("Model does not exists ")

    else:
        return redirect('signin')

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowerCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowerCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('profile/'+user)
        else:
            new_follower = FollowerCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('profile/'+user)

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)
        username_profile = []
        username_profile_lists = []

        for users in username_object:
            username_profile.append(users.id)
        
        for ids in username_profile:
            profile_list = Profile.objects.filter(id_user=ids)
            username_profile_lists.append(profile_list)

        username_profile_list = list(chain(*username_profile_lists))


    context = {
        'user_profile':user_profile,
        'username_profile_list':username_profile_list,
    }
    return render(request, 'search.html', context)

@login_required(login_url='signin')
def like_post(request):
        response_data = []
        if request.method == 'GET':
            username = request.user.username
            post_id = request.GET.get('post_id')

            post = Post.objects.get(id=post_id)

            like_exists = LikePost.objects.filter( post_id=post_id, username=username)

            if like_exists:
                like_exists.delete()
                post.no_of_likes = post.no_of_likes - 1 
                post.save()

                response_data ={
                    'key' : post_id,
                    'likes' : post.no_of_likes,
                    'status': 'unlike',
                }
                return JsonResponse(response_data, safe=False)
            else:
                new_like = LikePost.objects.create( post_id=post_id, username=username)
                new_like.save()
                post.no_of_likes = post.no_of_likes + 1
                Post.objects.filter(id=post_id).update(no_of_likes=post.no_of_likes)
                

                response_data ={
                    'key' : post_id,
                    'likes' : post.no_of_likes,
                    'status': 'liked',
                }
                   
                return JsonResponse(response_data, safe=False)
        return redirect('/')

@login_required(login_url='signin')
def profile(request, pk):
    try:
        user_object = User.objects.get(username=pk)
        user_profile = Profile.objects.get(user=user_object)
        user_posts = Post.objects.filter(user=pk)
        user_num_of_posts = len(user_posts)

       

        #Dynamic button for follow and unfollow
        if FollowerCount.objects.filter(follower=request.user.username, user=pk):
            button_text = 'unfollow'
        else:
            button_text = 'follow'

        user_followers = len(FollowerCount.objects.filter(user=pk))
        user_following = len(FollowerCount.objects.filter(follower=pk))

        context = {
            'user_object':user_object,
            'user_profile':user_profile,
            'user_posts':user_posts,
            'user_num_of_posts':user_num_of_posts,
            'button_text':button_text,
            'user_followers':user_followers,
            'user_following':user_following
        }

        return render(request, 'profile.html', context)
    except ObjectDoesNotExist:
        return HttpResponse("model does not exists")


@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        upload_user = request.user.username
        upload_image = request.FILES.get('upload_image')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=upload_user, post_image=upload_image, caption=caption)
        new_post.save()

        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def setting(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        if request.FILES.get('image'):
            profile_image = request.FILES.get('image')
            location = request.POST['location']
            bio = request.POST['bio']

            user_profile.profile_img = profile_image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        else:
            profile_image = user_profile.profile_img
            location = request.POST['location']
            bio = request.POST['bio']

            user_profile.profile_img = profile_image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        redirect('setting')

    return render (request, 'setting.html',{'user_profile':user_profile})

def signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        #check if password match
        if password == confirm_password:
            #check if email exists
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Already Exists')
                redirect('signup')
            #check if username exists
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Already Exists')
                redirect('signup')
            #create user
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #redirect user to settings url 
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create profile for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                
                return redirect('setting')
        else:
            messages.info(request, 'Password Mismatch')
            redirect('signup')
        
    return render(request, 'signup.html')

def signin(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if username and password :
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return redirect('/')
            else:
                messages.info(request, 'Invalid Credetials')
                return redirect('signin') 
        elif username or password:
            if username:
                messages.info(request, 'Password Must Be Filled')
                return redirect('/signin')
            else:
                messages.info(request, 'Username must be Filled')
                return redirect('/signin')
        else:
            messages.info(request, 'Please Enter Username and Password')
            return redirect('/signin')

            
    return render(request, 'signin.html')
    
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('/signin')