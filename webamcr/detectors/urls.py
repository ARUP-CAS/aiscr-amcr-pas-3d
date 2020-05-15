from django.urls import path

from . import views

app_name = 'pas'

urlpatterns = [
    path('', views.index, name="index"),
    path('create/', views.create, name="create"),
    path('create/<str:ident_cely>/', views.create, name="detail"),
    path('history/<str:ident_cely>/', views.historyDetectorsList, name="detectors_history"),
    path('choose/', views.choose, name="choose"),
    path('myfinds/', views.my_detectors, name='moje_list'),
    path('cooperate/', views.cooperate, name="cooperate"),
    path('cooperate/update/<int:pk>/', views.updateCooperation, name="cooparate_update"),
    path('cooperate/create/', views.createCooperation, name="cooparate_create"),
    path('cooperate/delete/<int:pk>/', views.deleteCooperation, name="cooparate_delete"),
    path('cooperate/history/<int:pk>/', views.historyCooperationList, name='cooperate_history'),
    path('confirm/', views.confirm, name="confirm"),  # list findings to be confirmed
    path('archive/', views.archive, name="archive"),  # list findings to be archived
    path('return/<str:ident_cely>/', views.return_finding, name="return_finding"),

    path('file/upload/<int:projectId>/<str:findingIdentCely>/', views.upload, name="upload"),
]
