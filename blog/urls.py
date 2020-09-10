from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'^$', views.main_page, name='todays_login1'),
    url(r'^login/$', views.result, name='todays_login'),
]
