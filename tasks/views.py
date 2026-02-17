from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from .forms import *
from django.conf import settings
from .tmdb import discover_tv_top10
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def signup(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = UserCreationForm()

    return render(request, "tasks/signup.html", {"form": form})

@login_required
def index(request):
    tasks = Task.objects.filter(user=request.user).order_by("-created")
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.platform = "MANUAL"
            task.provider_id = None
            task.save()
        return redirect('/')

    context = {'tasks': tasks, 'form': form}
    return render(request, 'tasks/list.html', context)


@login_required
def updateTask(request, pk):
    task = Task.objects.get(id=pk, user=request.user)
    form = TaskForm(instance=task)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('/')

    return render(request, 'tasks/update_task.html', {'form': form})

@login_required
def deleteTask(request, pk):
    item = Task.objects.get(id=pk, user=request.user)

    if request.method == "POST":
        item.delete()
        return redirect('/')

    return render(request, 'tasks/delete.html', {'item': item})

def _next_page(request, key: str) -> int:
    """
    Returns next page number for a given platform key stored in session.
    """
    session_key = f"tmdb_page_{key}"
    page = request.session.get(session_key, 1)
    request.session[session_key] = page + 1
    return page

@login_required
def import_netflix(request):
    if request.method != "POST":
        return redirect("/")

    page = _next_page(request, "NETFLIX")
    shows = discover_tv_top10(settings.TMDB_PROVIDER_NETFLIX, region=getattr(settings, "TMDB_REGION", "FR"), page=page)

    for s in shows:
        tmdb_id = s.get("id")
        if not tmdb_id:
            continue

        Task.objects.update_or_create(
            user=request.user,
            platform="NETFLIX",
            provider_id=tmdb_id,
            defaults={
                "title": s.get("name") or s.get("original_name") or "Untitled",
                "complete": False,
                "rating": s.get("vote_average"),
                "poster_url": f"https://image.tmdb.org/t/p/w500{s.get('poster_path')}" if s.get("poster_path") else None,
            },
        )

    return redirect("/")

@login_required()
def import_prime(request):
    if request.method != "POST":
        return redirect("/")

    page = _next_page(request, "PRIME")
    shows = discover_tv_top10(
        settings.TMDB_PROVIDER_PRIME,
        region=getattr(settings, "TMDB_REGION", "FR"),
        page=page,
    )

    for s in shows:
        tmdb_id = s.get("id")
        if not tmdb_id:
            continue

        Task.objects.update_or_create(
            user=request.user,
            platform="PRIME",
            provider_id=tmdb_id,
            defaults={
                "title": s.get("name") or s.get("original_name") or "Untitled",
                "complete": False,
                "rating": s.get("vote_average"),
                "poster_url": f"https://image.tmdb.org/t/p/w500{s.get('poster_path')}" if s.get("poster_path") else None,
            },
        )

    return redirect("/")

@login_required()
def import_apple(request):
    if request.method != "POST":
        return redirect("/")

    page = _next_page(request, "APPLE")
    shows = discover_tv_top10(
        settings.TMDB_PROVIDER_APPLE,
        region=getattr(settings, "TMDB_REGION", "FR"),
        page=page,
    )

    for s in shows:
        tmdb_id = s.get("id")
        if not tmdb_id:
            continue

        Task.objects.update_or_create(
            user=request.user,
            platform="APPLE",
            provider_id=tmdb_id,
            defaults={
                "title": s.get("name") or s.get("original_name") or "Untitled",
                "complete": False,
                "rating": s.get("vote_average"),
                "poster_url": f"https://image.tmdb.org/t/p/w500{s.get('poster_path')}" if s.get("poster_path") else None,
            },
        )

    return redirect("/")

@login_required
def delete_all(request):
    if request.method != "POST":
        return redirect("/")

    Task.objects.filter(user=request.user).delete()

    for key in ["tmdb_page_NETFLIX", "tmdb_page_PRIME", "tmdb_page_APPLE"]:
        request.session.pop(key, None)

    return redirect("/")
