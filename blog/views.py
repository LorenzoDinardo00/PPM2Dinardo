from datetime import date
from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from .models import Post
from django.views.generic import ListView, DetailView
from .form import CommentForm, UserRegisterForm, PostForm
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Author
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views 
from django.utils.text import slugify  # Assicurati che questa importazione sia presente
from django.contrib.auth import login  # Aggiungi questa linea


def get_date(post):
    return post['date']

class StartingPageView(ListView):
    template_name = "blog/index.html"
    model = Post
    ordering = ["-date"]
    context_object_name = "posts"

    def get_queryset(self):
        queryset = super().get_queryset()
        data = queryset[:3]
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user  # Passa l'oggetto utente al contesto
        return context

def custom_logout(request):
    logout(request)
    return redirect('login')

class AllPostsView(ListView):
    template_name = "blog/all-posts.html"
    model = Post
    ordering= ["-date"]
    context_object_name = "all_posts"


class SinglePostView(View):
    def is_stored_post(self, request,post_id):
        stored_posts = request.session.get("stored_posts")
        if stored_posts is not None:
            is_saved = post_id in stored_posts
        else:
            is_saved = False
        return is_saved


    template_name = "blog/post-detail.html"
    model = Post
    def get(self, request, slug):
        post = Post.objects.get(slug=slug)
        
        context = {
           "post": post,
           "post_tags": post.tags.all(),
           "comment_form": CommentForm(),
           "comments": post.comments.all().order_by("-id"),
           "saved": self.is_stored_post(request, post.id)

        }
        return render(request,"blog/post-detail.html", context)



    def post(self, request, slug):
        comment_form = CommentForm(request.POST)
        post = Post.objects.get(slug=slug)

        if comment_form.is_valid():
            comment = comment_form.save(commit = False)
            comment.post = post
            comment.save()
            return HttpResponseRedirect(reverse("post-detail-page", args = [slug]))
        
        
        context = {
            "post": post,
            "post_tags": post.tags.all(),
            "comment_form": CommentForm,
            "comments": post.comments.all().order_by("-id"),
            "saved": self.is_stored_post(request, post.id)

        }
        return render(request,"blog/post-detail.html",context)

class ReadLaterView(View):
    def get(self, request):
        stored_posts = request.session.get("stored_posts")
        context = {}
        if stored_posts is None or len(stored_posts)==0:
            context["posts"] = []
            context["has_posts"] = False
        else:
            posts = Post.objects.filter(id__in= stored_posts)
            context["posts"] = posts
            context["has_posts"] = True
        
        return render(request, "blog/stored-posts.html", context)


    def post(self, request):
        stored_posts = request.session.get("stored_posts")

        if stored_posts is None:
            stored_posts=[]
        post_id=int(request.POST["post_id"])
        if post_id not in stored_posts:
            stored_posts.append(post_id)
        else:
            stored_posts.remove(post_id)
        request.session["stored_posts"] = stored_posts

        return HttpResponseRedirect("/")
 
class CustomLoginView(auth_views.LoginView):
    template_name = 'blog/login.html'

    def form_valid(self, form):
        user = form.get_user()
        if not hasattr(user, 'author'):
            Author.objects.create(
                user=user,
                first_name=user.username,
                last_name='',
                email_address=user.email
            )
        return super().form_valid(form)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Author.objects.create(
                user=user,
                first_name=user.username,
                last_name='',
                email_address=user.email
            )
            login(request, user)
            return redirect('starting-page')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            if not hasattr(request.user, 'author'):
                author = Author.objects.create(
                    user=request.user,
                    first_name=request.user.username,
                    last_name='',
                    email_address=request.user.email
                )
            else:
                author = request.user.author
            post.author = author
            if not post.slug:
                post.slug = slugify(post.title)
                # Verifica se lo slug è unico
                unique_slug = post.slug
                num = 1
                while Post.objects.filter(slug=unique_slug).exists():
                    unique_slug = f"{post.slug}-{num}"
                    num += 1
                post.slug = unique_slug
            post.save()
            return redirect('starting-page')
    else:
        form = PostForm()
    return render(request, 'create_post.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('starting-page')