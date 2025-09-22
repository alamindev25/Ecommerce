
from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task-list'),               # home page / task list
    path('add/', views.add_task, name='add-task'),            # add task
    path('complete/<int:task_id>/', views.complete_task, name='complete-task'),  # complete
    path('delete/<int:task_id>/', views.delete_task, name='delete-task'),        # delete
]

