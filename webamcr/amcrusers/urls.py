from django.urls import path, register_converter
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# I have to make sure that django can map also negative pk for users objects
# (there is one user with negative id - i dont know why)


class NegativeIntConverter:
    regex = '-?\\d+'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '%d' % value


register_converter(NegativeIntConverter, 'negint')

app_name = 'amcrusers'

urlpatterns = [
    path('', views.userDetail, name='user_detail'),
    path('list/', views.users_list, name="users_list"),
    path('userList/', views.UsersList.as_view()),
    path('create/', views.user_create, name="user_create"),
    path('edit/<negint:pk>/', views.user_edit, name="user_edit"),
    path('delete/<negint:pk>/', views.user_delete, name="user_delete"),
]

urlpatterns += staticfiles_urlpatterns()
