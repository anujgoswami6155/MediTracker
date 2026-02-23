from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from core.decorators import role_required
from .models import Medicine, Prescription, PrescriptionItem
from .forms import MedicineForm, PrescriptionForm, PrescriptionItemForm


# ==========================================
# MEDICINE CATALOG (Anyone can view/add)
# ==========================================

@login_required
def medicine_list(request):
    """View all medicines in the catalog"""
    medicines = Medicine.objects.filter(is_active=True).order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        medicines = medicines.filter(
            Q(name__icontains=search_query) |
            Q(generic_name__icontains=search_query) |
            Q(manufacturer__icontains=search_query)
        )
    
    context = {
        'medicines': medicines,
        'search_query': search_query,
    }
    return render(request, 'medicines/medicine_list.html', context)


@login_required
def medicine_detail(request, pk):
    """View medicine details"""
    medicine = get_object_or_404(Medicine, pk=pk, is_active=True)
    
    # Get prescriptions using this medicine (if patient)
    my_prescriptions = []
    if request.user.role == 'patient':
        my_prescriptions = PrescriptionItem.objects.filter(
            medicine=medicine,
            prescription__patient=request.user,
            is_active=True
        ).select_related('prescription')
    
    context = {
        'medicine': medicine,
        'my_prescriptions': my_prescriptions,
    }
    return render(request, 'medicines/medicine_detail.html', context)


@login_required
def medicine_create(request):
    """Add new medicine to catalog"""
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('medicines:list')
    else:
        form = MedicineForm()
    
    return render(request, 'medicines/medicine_form.html', {
        'form': form,
        'title': 'Add New Medicine',
    })


@login_required
def medicine_edit(request, pk):
    """Edit medicine in catalog"""
    medicine = get_object_or_404(Medicine, pk=pk)
    
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            return redirect('medicines:detail', pk=medicine.pk)
    else:
        form = MedicineForm(instance=medicine)
    
    return render(request, 'medicines/medicine_form.html', {
        'form': form,
        'title': 'Edit Medicine',
        'medicine': medicine,
    })


@login_required
def medicine_delete(request, pk):
    """Soft delete medicine"""
    medicine = get_object_or_404(Medicine, pk=pk)
    
    if request.method == 'POST':
        medicine.is_active = False
        medicine.save()
        return redirect('medicines:list')
    
    return render(request, 'medicines/medicine_confirm_delete.html', {
        'medicine': medicine,
    })


# ==========================================
# PRESCRIPTIONS (Patient-specific)
# ==========================================

@role_required('patient')
def my_prescriptions(request):
    """View patient's prescriptions"""
    prescriptions = Prescription.objects.filter(
        patient=request.user
    ).prefetch_related('items__medicine').order_by('-created_at')
    
    return render(request, 'medicines/prescription_list.html', {
        'prescriptions': prescriptions,
    })


@role_required('patient')
def prescription_detail(request, pk):
    """View prescription details"""
    prescription = get_object_or_404(
        Prescription,
        pk=pk,
        patient=request.user
    )
    
    items = prescription.items.filter(is_active=True).select_related('medicine')
    
    return render(request, 'medicines/prescription_detail.html', {
        'prescription': prescription,
        'items': items,
    })


@role_required('patient')
def prescription_create(request):
    """Create new prescription"""
    if request.method == 'POST':
        form = PrescriptionForm(patient=request.user, data=request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.patient = request.user
            prescription.save()
            return redirect('medicines:prescription_detail', pk=prescription.pk)
    else:
        form = PrescriptionForm(patient=request.user)
    
    return render(request, 'medicines/prescription_form.html', {
        'form': form,
        'title': 'Create Prescription',
    })


@role_required('patient')
def add_medicine_to_prescription(request, prescription_pk):
    """Add medicine to existing prescription"""
    prescription = get_object_or_404(
        Prescription,
        pk=prescription_pk,
        patient=request.user
    )
    
    if request.method == 'POST':
        form = PrescriptionItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.prescription = prescription
            item.save()
            return redirect('medicines:prescription_detail', pk=prescription.pk)
    else:
        form = PrescriptionItemForm()
    
    return render(request, 'medicines/add_medicine_form.html', {
        'form': form,
        'prescription': prescription,
    })