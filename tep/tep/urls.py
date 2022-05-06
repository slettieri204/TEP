"""tep URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from tallyhq.views import TeacherLogin
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('admin/', admin.site.urls),
    path('tallyhq/', include('tallyhq.urls')),
    path('', TeacherLogin.as_view() ),  #send the '/'  url to the teacher login page

] 

#FOR LOCAL DEVELOPMENT(settings.PRODUCTION ==False), ADD THE MEDIA_URL TO THE MAIN URL PATTERNS
if settings.PRODUCTION ==False:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = 'tallyhq.views.custom_404_handler'
