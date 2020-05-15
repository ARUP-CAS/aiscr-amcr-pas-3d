from django.urls import path

from . import views

app_name = 'documents'

urlpatterns = [
	path('', views.index, name="index"),
	path('create/', views.create, name="create"),
	path('create/<str:ident_cely>/', views.create, name="detail"),
	path('mymodels/', views.my_models, name='my_models'),
	path('manage/', views.manage_models, name='manage_models'),
	path('choose/', views.choose, name="choose"),
	path('upload/<int:pk>/', views.upload_file, name="upload_file"),
	path('name/create/', views.name_create, name="create_name"),
	path('finding/create/<str:ident_cely>/', views.finding_create, name="create_finding"),  # ident of the docuemnt component
	path('finding/update/<int:pk>/', views.finding_update, name="update_finding"),
	path('finding/delete/<int:pk>/', views.finding_delete, name='delete_finding'),
	path('author/edit/<str:ident_cely>/', views.author_edit, name="edit_author"),  # ident of the model
	path('return/<str:ident_cely>/', views.return_model, name="return_model"),
	path('history/<str:ident_cely>/', views.model_history, name="documents_history"),

	# API
	path('download_file/<int:pk>/', views.download_file, name='download_file'),  # id of the file
]
