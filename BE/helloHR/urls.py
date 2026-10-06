"""
URL configuration for helloHR project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from accounts import views as account_views
from django.contrib import admin
from django.urls import path
from trainings import views as training_views
from trainings import participants as participant_views
from attendance import views as attendance_views
from reports import views as report_views

urlpatterns = [
    path('api/accounts/session/', account_views.session),
    path('api/accounts/signup/', account_views.signup),
    path('api/accounts/login/', account_views.signin),
    path('api/accounts/logout/', account_views.signout),
    path('api/trainings/<int:training_id>/public/', training_views.public_training),
    path('admin/', admin.site.urls),
    path('api/csrf/', training_views.csrf_token, name='api-csrf'),
    path('api/trainings/<int:training_id>/report/', report_views.training_report, name='training-report'),
    path('api/trainings/<int:training_id>/check-in/', attendance_views.check_in, name='check-in'),
    path('api/participants/<int:participant_id>/attendance/', attendance_views.set_attendance, name='set-attendance'),
    path('api/trainings/', training_views.training_list, name='training-list'),
    path('api/trainings/<int:training_id>/', training_views.training_detail, name='training-detail'),
    path('api/trainings/<int:training_id>/participants/', participant_views.participant_list, name='participant-list'),
    path('api/trainings/<int:training_id>/participants/<int:participant_id>/', participant_views.participant_detail, name='participant-detail'),
    path('api/trainings/<int:training_id>/participants/upload/', participant_views.participant_upload, name='participant-upload'),
    path('api/participants/template/', participant_views.participant_template, name='participant-template'),
]
