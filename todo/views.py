from django.shortcuts import render, redirect
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