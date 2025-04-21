from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Q, Max, F, Count
from .models import Profile, Tweet, Comment, Notification, Message
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, TweetForm, CommentForm, MessageForm

# Create your views here.

def register(request):
    if request.method == 'POST':
        # Get form data directly from POST
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic validation
        if not (username and email and password1 and password2):
            messages.error(request, 'Please fill in all fields')
            return render(request, 'core/register.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'core/register.html')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'core/register.html')

        # Create user
        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')

    return render(request, 'core/register.html')

@login_required
def home(request):
    # Get tweets from users that the current user follows
    following_users = request.user.profile.following.values_list('user', flat=True)
    tweets = Tweet.objects.filter(user__in=following_users) | Tweet.objects.filter(user=request.user)

    # Handle new tweet creation
    if request.method == 'POST':
        tweet_form = TweetForm(request.POST, request.FILES)
        if tweet_form.is_valid():
            tweet = tweet_form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            messages.success(request, 'Your tweet has been posted!')
            return redirect('home')
    else:
        tweet_form = TweetForm()

    context = {
        'tweets': tweets,
        'tweet_form': tweet_form
    }
    return render(request, 'core/home.html', context)

@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    tweets = Tweet.objects.filter(user=user)

    # Get tweets liked by the user
    liked_tweets = Tweet.objects.filter(likes=user)

    # Check if current user follows this profile
    is_following = False
    if request.user.is_authenticated:
        is_following = request.user.profile.following.filter(user=user).exists()

    context = {
        'user_profile': user,
        'tweets': tweets,
        'liked_tweets': liked_tweets,
        'is_following': is_following
    }
    return render(request, 'core/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Get form data directly from POST
        username = request.POST.get('username')
        email = request.POST.get('email')
        bio = request.POST.get('bio')
        location = request.POST.get('location')
        birth_date = request.POST.get('birth_date')

        # Update user info
        user = request.user
        user.username = username
        user.email = email
        user.save()

        # Update profile info
        profile = user.profile
        profile.bio = bio
        profile.location = location
        if birth_date:
            profile.birth_date = birth_date

        # Handle profile picture upload
        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']

        profile.save()

        messages.success(request, 'Your profile has been updated!')
        return redirect('profile', username=user.username)

    return render(request, 'core/edit_profile.html')

@login_required
def follow_toggle(request, username):
    user_to_toggle = get_object_or_404(User, username=username)

    # Don't allow users to follow themselves
    if request.user == user_to_toggle:
        return redirect('profile', username=username)

    if request.user.profile.following.filter(user=user_to_toggle).exists():
        # Unfollow
        request.user.profile.following.remove(user_to_toggle.profile)
        is_following = False
    else:
        # Follow
        request.user.profile.following.add(user_to_toggle.profile)
        is_following = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'is_following': is_following})

    return redirect('profile', username=username)

@login_required
def like_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)

    if tweet.likes.filter(id=request.user.id).exists():
        # Unlike
        tweet.likes.remove(request.user)
        liked = False
    else:
        # Like
        tweet.likes.add(request.user)
        liked = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': tweet.total_likes()})

    return redirect('home')

def explore(request):
    # Show all tweets from all users
    tweets = Tweet.objects.all()

    # Get all users for the "Who to follow" section
    users = User.objects.exclude(id=request.user.id) if request.user.is_authenticated else User.objects.all()
    users = users[:5]  # Limit to 5 users

    context = {
        'tweets': tweets,
        'suggested_users': users
    }
    return render(request, 'core/explore.html', context)

@login_required
def tweet_detail(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    comments = tweet.comments.all()

    # Handle new comment creation
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.tweet = tweet
            comment.user = request.user
            comment.save()
            messages.success(request, 'Your comment has been posted!')
            return redirect('tweet_detail', tweet_id=tweet.id)
    else:
        comment_form = CommentForm()

    context = {
        'tweet': tweet,
        'comments': comments,
        'comment_form': comment_form
    }
    return render(request, 'core/tweet_detail.html', context)

@login_required
def retweet(request, tweet_id):
    original_tweet = get_object_or_404(Tweet, id=tweet_id)

    # Check if user has already retweeted this tweet
    if Tweet.objects.filter(user=request.user, is_retweet=True, original_tweet=original_tweet).exists():
        messages.warning(request, 'You have already retweeted this tweet!')
        return redirect('home')

    # Create retweet
    retweet = Tweet(
        user=request.user,
        content=original_tweet.content,
        is_retweet=True,
        original_tweet=original_tweet
    )

    # Copy image if exists
    if original_tweet.image:
        retweet.image = original_tweet.image

    retweet.save()
    messages.success(request, 'Tweet has been retweeted!')

    return redirect('home')

@login_required
def followers_list(request, username):
    user = get_object_or_404(User, username=username)
    followers = user.profile.followers.all()

    context = {
        'user_profile': user,
        'followers': followers,
        'list_type': 'Followers'
    }
    return render(request, 'core/user_list.html', context)

@login_required
def following_list(request, username):
    user = get_object_or_404(User, username=username)
    following = user.profile.following.all()

    context = {
        'user_profile': user,
        'following': following,
        'list_type': 'Following'
    }
    return render(request, 'core/user_list.html', context)

@login_required
def share_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)

    if request.method == 'POST':
        recipient_ids = request.POST.getlist('recipients')
        recipients = User.objects.filter(id__in=recipient_ids)

        for recipient in recipients:
            # Create notification for each recipient
            Notification.objects.create(
                recipient=recipient,
                sender=request.user,
                notification_type='share',
                tweet=tweet
            )

        messages.success(request, f'Tweet shared with {len(recipients)} followers!')
        return redirect('tweet_detail', tweet_id=tweet.id)

    # Get users that the current user follows
    following_users = request.user.profile.following.values_list('user', flat=True)
    following_users = User.objects.filter(id__in=following_users)

    context = {
        'tweet': tweet,
        'following_users': following_users
    }
    return render(request, 'core/share_tweet.html', context)

@login_required
def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user)

    # Mark all as read
    if request.method == 'POST':
        notifications.update(is_read=True)
        return redirect('notifications')

    context = {
        'notifications': notifications
    }
    return render(request, 'core/notifications.html', context)

@login_required
def inbox(request):
    # Get all users that the current user has had conversations with
    conversations = Message.get_conversations(request.user)

    # Get the latest message from each conversation
    latest_messages = []
    for user in conversations:
        latest_message = Message.objects.filter(
            (Q(sender=request.user) & Q(recipient=user)) |
            (Q(sender=user) & Q(recipient=request.user))
        ).order_by('-created_at').first()

        if latest_message:
            latest_messages.append({
                'user': user,
                'message': latest_message,
                'unread_count': Message.objects.filter(sender=user, recipient=request.user, is_read=False).count()
            })

    # Sort by latest message
    latest_messages.sort(key=lambda x: x['message'].created_at, reverse=True)

    context = {
        'conversations': latest_messages
    }
    return render(request, 'core/inbox.html', context)

@login_required
def conversation(request, username):
    other_user = get_object_or_404(User, username=username)

    # Get all messages between the two users
    messages_list = Message.get_conversation(request.user, other_user)

    # Mark messages as read
    messages_list.filter(sender=other_user, recipient=request.user, is_read=False).update(is_read=True)

    # Handle new message
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = other_user
            message.save()

            # Create notification for the recipient
            Notification.objects.create(
                recipient=other_user,
                sender=request.user,
                notification_type='message'
            )

            return redirect('conversation', username=username)
    else:
        form = MessageForm()

    context = {
        'other_user': other_user,
        'messages_list': messages_list,
        'form': form
    }
    return render(request, 'core/conversation.html', context)
