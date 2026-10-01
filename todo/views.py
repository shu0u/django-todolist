from django.shortcuts import render, redirect, get_object_or_404
from todo.models import Task

def home(request):
    if request.method == "POST":
        task_title = request.POST.get('title')

        if task_title:
            Task.objects.create(title=task_title)

        return redirect('home')
    
    tasks = Task.objects.all().order_by('-created_at')

    context = {
        'tasks': tasks
    }

    return render(request, 'index.html', context)

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('home')

def toggle_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.completed = not task.completed
    task.save()
    return redirect('home')

def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        new_title = request.POST.get('title')
        if new_title:
            task.title = new_title
            task.save()
            return redirect('home')
    return render(request, 'edit.html', {'task': task})