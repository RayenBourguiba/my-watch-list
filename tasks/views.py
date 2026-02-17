from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from .forms import *
from django.conf import settings
from .tmdb import discover_tv_top10
from django.views.decorators.http import require_POST

# Create your views here.
def index(request):
	tasks = Task.objects.all()

	form = TaskForm()

	if request.method == 'POST':
		form = TaskForm(request.POST)
		if form.is_valid():
			#adds to the database if valid
			form.save()
		return redirect('/')

	context= {'tasks':tasks,'form':form}
	return render(request, 'tasks/list.html',context)

def updateTask(request,pk):
	task = Task.objects.get(id=pk)
	form = TaskForm(instance=task)

	if request.method == "POST":
		form = TaskForm(request.POST,instance=task)
		if form.is_valid():
			form.save()
			return redirect('/')


	context = {'form':form}
	return render(request, 'tasks/update_task.html',context)

def deleteTask(request,pk):
	item = Task.objects.get(id=pk)

	if request.method == "POST":
		item.delete()
		return redirect('/')

	context = {'item':item}
	return render(request, 'tasks/delete.html', context)

def _next_page(request, key: str) -> int:
    """
    Returns next page number for a given platform key stored in session.
    """
    session_key = f"tmdb_page_{key}"
    page = request.session.get(session_key, 1)
    request.session[session_key] = page + 1
    return page

def import_netflix(request):
    if request.method != "POST":
        return redirect("/")

    page = _next_page(request, "NETFLIX")
    shows = discover_tv_top10(
        settings.TMDB_PROVIDER_NETFLIX,
        region=getattr(settings, "TMDB_REGION", "FR"),
        page=page,
    )

    for s in shows:
        tmdb_id = s.get("id")
        if not tmdb_id:
            continue

        Task.objects.update_or_create(
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

@require_POST
def delete_all(request):
    Task.objects.all().delete()
    # optional: reset pagination so next import starts at page 1 again
    for key in ["tmdb_page_NETFLIX", "tmdb_page_PRIME", "tmdb_page_APPLE"]:
        request.session.pop(key, None)
    return redirect("/")
