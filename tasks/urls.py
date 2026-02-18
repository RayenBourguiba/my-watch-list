from django.urls import path
from . import views
urlpatterns = [
	path('', views.index, name="list"),
	path('update_task/<str:pk>/', views.updateTask, name="update_task"),
	path('delete_task/<str:pk>/', views.deleteTask, name="delete"),

	path("import/netflix/", views.import_netflix, name="import_netflix"),
    path("import/prime/", views.import_prime, name="import_prime"),
    path("import/apple/", views.import_apple, name="import_apple"),
	path("delete-all/", views.delete_all, name="delete_all"),
	path("franceconnect/login/", views.franceconnect_login, name="fc_login"),
	path("callback", views.franceconnect_callback, name="fc_callback"),
	path("google/login/", views.google_login, name="google_login"),
	path("google/callback/", views.google_callback, name="google_callback"),
]