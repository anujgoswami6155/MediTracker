from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from .models import MedicalDocument
from .forms import MedicalDocumentForm


# ==========================
# UPLOAD DOCUMENT (PATIENT)
# ==========================
@login_required
@role_required("patient")
def upload_document(request):
    if request.method == "POST":
        form = MedicalDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            return redirect("documents:list")
    else:
        form = MedicalDocumentForm()

    return render(request, "documents/upload.html", {
        "form": form
    })


# ==========================
# DOCUMENT LIST
# ==========================
@login_required
def document_list(request):
    user = request.user

    if user.role == "patient":
        documents = MedicalDocument.objects.filter(
            patient=user,
            is_active=True
        )

    elif user.role in ["doctor", "family"]:
        documents = MedicalDocument.objects.filter(is_active=True)

    else:
        documents = MedicalDocument.objects.none()

    return render(request, "documents/list.html", {
        "documents": documents
    })


# ==========================
# DOCUMENT DETAIL
# ==========================
@login_required
def document_detail(request, pk):
    document = get_object_or_404(
        MedicalDocument,
        pk=pk,
        is_active=True
    )

    return render(request, "documents/detail.html", {
        "document": document
    })


# ==========================
# DELETE DOCUMENT (SOFT DELETE)
# ==========================
@login_required
@role_required("patient")
def delete_document(request, pk):
    document = get_object_or_404(
        MedicalDocument,
        pk=pk,
        patient=request.user
    )

    if request.method == "POST":
        document.is_active = False
        document.save(update_fields=["is_active"])
        return redirect("documents:list")

    return render(request, "documents/confirm_delete.html", {
        "document": document
    })
