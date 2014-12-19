from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = patterns(
    '',
    url(r'^v0/', include('course_api.v0.urls', namespace='v0')),
)

urlpatterns = format_suffix_patterns(urlpatterns)
