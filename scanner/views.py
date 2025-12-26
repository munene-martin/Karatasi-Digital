import cv2
import numpy as np
import pytesseract
import json
import io 
from PIL import Image

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.http import HttpResponse, JsonResponse 
from django.views.decorators.csrf import csrf_exempt 

from scanner.models import Document
from .mpesa import initiate_stk_push

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# --- AUTH ---
def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('upload_scan')
    return render(request, 'scanner/signup.html', {'form': UserCreationForm()})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('upload_scan')
    return render(request, 'scanner/login.html', {'form': AuthenticationForm()})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- MAIN DASHBOARD & OCR ---
@login_required(login_url='login')
def upload_and_scan(request):
    document = None
    query = request.GET.get('q')
    
    if request.method == 'POST' and request.FILES.get('image_file'):
        title = request.POST.get('title')
        image_file = request.FILES.get('image_file')

        doc = Document.objects.create(user=request.user, title=title, image=image_file)

        # Better OCR Pre-processing
        img = cv2.imread(doc.image.path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        processed_img = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        text = pytesseract.image_to_string(Image.fromarray(processed_img), lang='eng+swa')
        doc.extracted_text = text.strip()
        doc.save()
        document = doc

    history = Document.objects.filter(user=request.user).order_by('-uploaded_at')
    if query:
        history = history.filter(title__icontains=query)

    return render(request, 'scanner/upload.html', {'document': document, 'history': history})

# --- MPESA & PAYMENTS ---
@login_required(login_url='login')
def pay_for_scan(request, doc_id): 
    document = get_object_or_404(Document, id=doc_id, user=request.user)
    if request.method == "POST":
        phone = request.POST.get('phone', '').strip().replace('+', '')
        response = initiate_stk_push(phone, 1) 
        if response.get('ResponseCode') == '0':
            document.checkout_request_id = response.get('CheckoutRequestID')
            document.save()
            return render(request, 'scanner/payment_status.html', {'status': 'Success', 'doc_id': doc_id})
    return redirect('upload_scan')

@csrf_exempt
def mpesa_callback(request):
    if request.method == "POST":
        data = json.loads(request.body)
        stk_callback = data['Body']['stkCallback']
        if stk_callback['ResultCode'] == 0:
            doc = Document.objects.filter(checkout_request_id=stk_callback['CheckoutRequestID']).first()
            if doc:
                items = stk_callback['CallbackMetadata']['Item']
                doc.mpesa_receipt = next(i['Value'] for i in items if i['Name'] == 'MpesaReceiptNumber')
                doc.is_paid = True
                doc.save()
        return HttpResponse(status=200)

@login_required
def check_payment_status(request, doc_id):
    document = get_object_or_404(Document, id=doc_id, user=request.user)
    return JsonResponse({'is_paid': document.is_paid})

# --- DOWNLOADS & ADMIN ---
@login_required
def download_pdf(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id, user=request.user, is_paid=True)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.drawString(100, 750, f"KARATASI DIGITAL - {doc.title}")
    p.drawString(100, 730, f"Receipt: {doc.mpesa_receipt}")
    
    to = p.beginText(100, 700)
    for line in doc.extracted_text.split('\n'):
        to.textLine(line)
    p.drawText(to)
    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

@login_required
def contact_view(request):
    if request.method == "POST":
        # Placeholder for email logic
        return redirect('upload_scan')
    return redirect('upload_scan')