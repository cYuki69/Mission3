from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .forms import MissionCommandForm, MissionSubmissionForm
from .models import Mission

def upload_image(request):
    missions = Mission.objects.order_by('-created_at')
    return render(request, 'uploads/upload.html', {'missions': missions})

def success_view(request):
    return render(request, 'uploads/success.html')


@staff_member_required(login_url='/admin/login/')
def create_mission(request):
    if request.method == 'POST':
        form = MissionCommandForm(request.POST)
        if form.is_valid():
            mission = Mission.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['command'],
                deadline=form.cleaned_data['deadline'],
            )
            return redirect('mission_submit', mission_id=mission.id)
    else:
        form = MissionCommandForm()

    missions = Mission.objects.order_by('-created_at')
    return render(request, 'uploads/create_mission.html', {
        'form': form,
        'missions': missions,
    })

def mission_submit(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id)
    
    # Check if already completed
    if mission.status == Mission.Status.COMPLETED:
        messages.info(request, "This mission has already been completed.")
        return render(request, 'uploads/mission_submit.html', {'mission': mission, 'completed': True})
    
    # Check if overdue
    if timezone.now() > mission.deadline and mission.status != Mission.Status.COMPLETED:
        if mission.status != Mission.Status.OVERDUE:
            mission.status = Mission.Status.OVERDUE
            mission.save()
        messages.error(request, "The deadline for this mission has passed.")
        return render(request, 'uploads/mission_submit.html', {'mission': mission, 'overdue': True})

    if request.method == 'POST':
        form = MissionSubmissionForm(request.POST, request.FILES, instance=mission)
        if form.is_valid():
            mission = form.save(commit=False)
            mission.status = Mission.Status.COMPLETED
            mission.save()
            messages.success(request, "Mission completed successfully!")
            return redirect('mission_submit', mission_id=mission.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MissionSubmissionForm(instance=mission)
        
    return render(request, 'uploads/mission_submit.html', {'form': form, 'mission': mission})
