from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from .models import Event, Review, Participant
from .forms import EventForm

def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    is_registered = Participant.objects.filter(event=event, user=request.user).exists()
    reviews = event.reviews.all()
    total_registrations = Participant.objects.filter(event=event).count()
    free_slots = max(0, event.slots_limit - total_registrations)
    
    context = {
        'event': event,
        'is_registered': is_registered,
        'reviews': reviews,
        'free_slots': free_slots,
    }
    return render(request, 'events/event_detail.html', context)

@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'is_update': False})

@login_required
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', pk=pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'events/event_form.html', {'form': form, 'event': event, 'is_update': True})

@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        return redirect('event_list')
    return render(request, 'events/event_confirm_delete.html', {'event': event})

@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    event_id = review.event.pk
    if review.user == request.user:
        review.delete()
    return redirect('event_detail', pk=event_id)

@login_required
def register_for_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    total_registrations = Participant.objects.filter(event=event).count()
    free_slots = max(0, event.slots_limit - total_registrations)
    
    if free_slots > 0:
        Participant.objects.get_or_create(
            event=event, 
            user=request.user,
            defaults={
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email or "user@example.com"
            }
        )
    return redirect('event_detail', pk=pk)

@login_required
def cancel_registration(request, pk):
    event = get_object_or_404(Event, pk=pk)
    Participant.objects.filter(event=event, user=request.user).delete()
    return redirect('event_detail', pk=pk)

@login_required
def my_registrations(request):
    registrations = Participant.objects.filter(user=request.user)
    return render(request, 'events/my_registrations.html', {'registrations': registrations})

@login_required
def toggle_favorite(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user in event.favorites.all():
        event.favorites.remove(request.user)
    else:
        event.favorites.add(request.user)
    return redirect('event_detail', pk=pk)

@login_required
def generate_pdf_ticket(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if not Participant.objects.filter(event=event, user=request.user).exists():
        return redirect('event_detail', pk=pk)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, f"Ticket for Event: {event.name}")
    p.drawString(100, 780, f"Participant: {request.user.username}")
    p.drawString(100, 760, f"Price: {event.price} UAH")
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"ticket_{event.pk}.pdf")