from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_image, name='upload_image'),
    path('success/', views.success_view, name='success'),
    path('missions/', views.create_mission, name='create_mission'),
    path('mission/create/', views.create_mission),
    path('mission/<uuid:mission_id>/', views.mission_submit, name='mission_submit'),
]
