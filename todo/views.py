from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from todo.models import Task

@login_required
def home(request):
    if request.method == "POST":
        task_title = request.POST.get('title')

        if task_title:
            Task.objects.create(title=task_title, user=request.user)

        return redirect('home')
    
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'tasks': tasks
    }

    return render(request, 'index.html', context)

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect('home')

@login_required
def toggle_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.completed = not task.completed
    task.save()
    return redirect('home')

@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        new_title = request.POST.get('title')
        if new_title:
            task.title = new_title
            task.save()
            return redirect('home')
    return render(request, 'edit.html', {'task': task})

