from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

from .models import Job, Notification, Profile
from .forms import JobForm, ProfileForm


def home(request):
    if request.user.is_authenticated:
        notifications = request.user.notifications.all().order_by('-created_at')[:5]
    else:
        notifications = []

    query = request.GET.get('q')

    if query:
        jobs = Job.objects.filter(
            Q(title__icontains=query) |
            Q(county__icontains=query) |
            Q(description__icontains=query)
        ).order_by('-created_at')
    else:
        jobs = Job.objects.all().order_by('-created_at')

    return render(request, 'jobs/home.html', {
        'jobs': jobs,
        'query': query,
        'notifications': notifications
    })


@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()

            # Notify all other users
            users = User.objects.exclude(id=request.user.id)
            for user in users:
                Notification.objects.create(
                    user=user,
                    message=f"New job posted: {job.title}"
                )

            messages.success(request, "Job posted successfully!")
            return redirect('home')
    else:
        form = JobForm()

    return render(request, 'jobs/post_job.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'jobs/register.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'jobs/login.html', {'error': 'All fields required'})

        user = authenticate(request, username=username, password=password)

        if user is not None:
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'jobs/login.html', {'error': 'Invalid credentials'})

    return render(request, 'jobs/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if job.posted_by != request.user:
        messages.error(request, "You are not allowed to delete this job.")
        return redirect('home')

    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job deleted successfully.")
        return redirect('home')

    return render(request, 'jobs/confirm_delete.html', {'job': job})


@login_required
def save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.user in job.saved_by.all():
        job.saved_by.remove(request.user)
        messages.info(request, "Job removed from saved.")
    else:
        job.saved_by.add(request.user)
        messages.success(request, "Job saved successfully!")

        # Notification when saving
        Notification.objects.create(
            user=request.user,
            message=f"You saved {job.title}"
        )

    return redirect('home')


@login_required
def saved_jobs(request):
    jobs = request.user.saved_jobs.all()
    return render(request, 'jobs/saved_jobs.html', {'jobs': jobs})


@login_required
def profile(request):
    return render(request, 'jobs/profile.html')


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'jobs/edit_profile.html', {'form': form})


@login_required
def toggle_dark_mode(request):
    if request.method == 'POST':
        user_profile = request.user.profile
        user_profile.dark_mode = 'dark_mode' in request.POST
        user_profile.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def notifications_view(request):
    notifications = request.user.notifications.all().order_by('-created_at')

    # Mark all as read
    notifications.update(is_read=True)

    return render(request, 'jobs/notifications.html', {
        'notifications': notifications
    })


@login_required
def mark_notifications_read(request):
    request.user.notifications.update(is_read=True)
    return redirect('home')