from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Post, Comment, Profile


# -----------------------------
# Home View (Post + Search)
# -----------------------------
@login_required
def home(request):

    # Create Post
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Post.objects.create(
                user=request.user,
                content=content
            )
            return redirect("home")

    # Search Feature
    query = request.GET.get("q")

    if query:
        posts = Post.objects.filter(
            Q(content__icontains=query) |
            Q(user__username__icontains=query)
        ).order_by("-created_at")
    else:
        posts = Post.objects.all().order_by("-created_at")

    return render(request, "posts/home.html", {
        "posts": posts
    })


# -----------------------------
# Delete Post
# -----------------------------
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user == request.user:
        post.delete()

    return redirect("home")


# -----------------------------
# Like Post
# -----------------------------
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return redirect("home")


# -----------------------------
# Profile View
# -----------------------------
@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=profile_user).order_by("-created_at")

    is_following = False
    if request.user in profile_user.profile.followers.all():
        is_following = True

    return render(request, "posts/profile.html", {
        "profile_user": profile_user,
        "posts": posts,
        "is_following": is_following
    })


# -----------------------------
# Add Comment
# -----------------------------
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Comment.objects.create(
                post=post,
                user=request.user,
                content=content
            )

    return redirect("home")


# -----------------------------
# Follow / Unfollow User
# -----------------------------
@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)

    if user_to_follow != request.user:
        profile = user_to_follow.profile

        if request.user in profile.followers.all():
            profile.followers.remove(request.user)
        else:
            profile.followers.add(request.user)

    return redirect('profile', username=username)