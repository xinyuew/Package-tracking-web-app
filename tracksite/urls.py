"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'tracksite.views.welcome', name='welcome'),
    url(r'^error$', 'tracksite.views.error_page', name='error'),
    url(r'^query$', 'tracksite.views.query', name='query'),
    url(r'^query/(?P<num>[a-zA-Z0-9]+)$', 'tracksite.views.query_with_num', name='query_with_num'),
    url(r'^add_track', 'tracksite.views.add_track', name='add_track'),
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name': 'tracksite/login.html'}, name='login'),
    url(r'^logout$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^register$', 'tracksite.views.register', name='register'),
    url(r'^profile$', 'tracksite.views.profile', name='profile'),
    url(r'^edit_profile', 'tracksite.views.edit_profile', name='edit_profile'),
    url(r'^photo/(?P<user_id>\d+)$', 'tracksite.views.get_photo', name='photo'),
    url(r'^roommate', 'tracksite.views.add_roommate', name='add_roommate'),
    url(r'^check_delivery$', 'tracksite.views.find_upcoming_delivery', name='check_delivery'),
    url(r'^send_email/(?P<user_id>\d+)$', 'tracksite.views.send_email', name='send_email'),
    url(
        r'^verify_add_roommate/(?P<username>[a-zA-Z0-9]+)/(?P<token>[a-zA-Z0-9_\-]+)/(?P<request_username>[a-zA-Z0-9]+)/$',
        'tracksite.views.verify_add_roommate', name='verify_add_roommate'),
    url(r'^add_as_roommate$', 'tracksite.views.add_as_roommate', name='add_as_roommate'),
    url(r'^remove_roommate/(?P<user_id>\d+)$', 'tracksite.views.remove_roommate', name='remove_roommate'),
    url(r'^delete_track/(?P<track_id>\d+)$', 'tracksite.views.delete_track', name='delete_track'),
]
