from django.urls import path, include
from .views import *

urlpatterns = [
    path('', login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('approve/<int:video_id>/<int:comment_id>/', approve),
    path('delete/<int:video_id>/<int:comment_id>/', delete),

    #User Dashboard
    path('Userdashboard/', user_dashboard),
]