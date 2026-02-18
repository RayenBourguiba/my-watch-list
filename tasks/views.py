from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.conf import settings
from .tmdb import discover_tv_top10
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
import uuid
import requests
from urllib.parse import urlencode
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http import HttpResponse

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

def franceconnect_login(request):
    state = uuid.uuid4().hex
    nonce = uuid.uuid4().hex  # 32 chars, ok

    request.session["fc_state"] = state
    request.session["fc_nonce"] = nonce

    params = {
        "response_type": "code",
        "client_id": settings.FRANCECONNECT_CLIENT_ID,
        "redirect_uri": settings.FRANCECONNECT_REDIRECT_URI,
        "scope": "openid profile email",
        "state": state,
        "nonce": nonce,
        "prompt": "login",
    }

    return redirect(f"{settings.FRANCECONNECT_AUTHORIZE_URL}?{urlencode(params)}")

def franceconnect_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")

    if not code:
        return redirect("/login/")

    if state != request.session.get("fc_state"):
        return HttpResponse("Invalid state", status=400)

    token_resp = requests.post(
        settings.FRANCECONNECT_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.FRANCECONNECT_REDIRECT_URI,
            "client_id": settings.FRANCECONNECT_CLIENT_ID,
            "client_secret": settings.FRANCECONNECT_CLIENT_SECRET,
        },
        timeout=10,
    )
    token_resp.raise_for_status()
    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return HttpResponse("No access_token", status=400)

    userinfo_resp = requests.get(
        settings.FRANCECONNECT_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    userinfo_resp.raise_for_status()
    userinfo = userinfo_resp.json()

    sub = userinfo.get("sub")
    email = userinfo.get("email", "")

    if not sub:
        return HttpResponse("No sub in userinfo", status=400)

    user, _ = User.objects.get_or_create(
        username=f"fc_{sub}",
        defaults={"email": email},
    )
    login(request, user)
    return redirect("/")


def google_login(request):
    state = uuid.uuid4().hex
    request.session["google_state"] = state

    params = {
        "response_type": "code",
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
        "access_type": "offline",
    }
    return redirect(f"{settings.GOOGLE_OAUTH_AUTHORIZE_URL}?{urlencode(params)}")


def google_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")

    if not code:
        return redirect("/login/")

    if state != request.session.get("google_state"):
        return HttpResponse("Invalid state", status=400)

    token_resp = requests.post(
        settings.GOOGLE_OAUTH_TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )
    token_resp.raise_for_status()
    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    if not access_token:
        return HttpResponse("No access_token", status=400)

    userinfo_resp = requests.get(
        settings.GOOGLE_OAUTH_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )
    userinfo_resp.raise_for_status()
    info = userinfo_resp.json()

    sub = info.get("sub")          # unique Google user id
    email = info.get("email", "")
    given = info.get("given_name", "")
    family = info.get("family_name", "")

    if not sub:
        return HttpResponse("No sub in userinfo", status=400)

    username = f"google_{sub}"
    user, created = User.objects.get_or_create(username=username, defaults={"email": email})

    # optionnel: mettre un nom la 1ère fois
    if created:
        user.first_name = given
        user.last_name = family
        user.save()

    login(request, user)
    return redirect("/")
