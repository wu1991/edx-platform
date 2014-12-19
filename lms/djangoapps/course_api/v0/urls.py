from django.conf import settings
from django.conf.urls import url, patterns, include
from course_api.v0 import views

COURSE_URLS = patterns(
    '',
    url(r'^$', views.CourseDetail.as_view(), name='detail'),
    url(r'^assignments/$', views.CourseAssignments.as_view(), name='assignments'),
)

urlpatterns = patterns(
    '',
    url('^$', views.CourseList.as_view(), name='list'),
    url(r'^{}/'.format(settings.COURSE_ID_PATTERN), include(COURSE_URLS))
)
