
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task


def task_list(request):
    tasks = Task.objects.all().order_by('-created')
    return render(request, 'notebook/task_list.html', {'tasks': tasks})


def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            Task.objects.create(title=title)
        return redirect('task-list')
   
    #  GET request 
    return render(request, 'notebook/add_task.html')


def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.completed = True
    task.save()
    return redirect('task-list')


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('task-list')

