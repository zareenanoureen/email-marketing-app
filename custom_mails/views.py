from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import SentEmail, ReceivedEmail
from django.views.decorators.csrf import csrf_exempt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import requests
from django.template.loader import render_to_string
from dotenv import load_dotenv
load_dotenv()

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
FROM_EMAIL = 'info@learnity.store'

def send_email(api_key, from_email, to_emails, subject, content):
    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=content)
    try:
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        return response.status_code, response.body, response.headers
    except Exception as e:
        return 500, str(e), {}  # Return a generic status code and error message

@csrf_exempt
def send_mail(request):
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        subject = request.POST.get('subject')
        html_body = request.POST.get('html_body')

        status_code, response_body, response_headers = send_email(
            SENDGRID_API_KEY, FROM_EMAIL, recipient, subject, html_body
        )

        if status_code == 202:
            # Assuming you have a SentEmail model defined
            SentEmail.objects.create(
                recipient=recipient,
                subject=subject,
                html_body=html_body
            )
            return HttpResponse("Email sent successfully", status=202)
        else:
            return HttpResponse(response_body, status=status_code)
    return render(request, 'dashboard/send_mail.html')

@csrf_exempt
def receive_mail(request):
    if request.method == 'POST':
        sender = request.POST.get('sender')
        subject = request.POST.get('subject')
        content = request.POST.get('content')

        if not content:
            return HttpResponse("Email content is empty", status=400)

        html_content = render_to_string('dashboard/received_mail.html', {
            'sender': sender,
            'subject': subject,
            'content': content
        })

        ReceivedEmail.objects.create(
            sender=sender,
            subject=subject,
            content=content
        )

        return HttpResponse(html_content)

    return render(request, 'dashboard/receive_mail.html')

@csrf_exempt
def reply_to_email(request):
    if request.method == 'POST':
        sender = request.POST.get('sender')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        recipient = request.POST.get('recipient')

        reply_content = f"Reply to: {sender}\n\n{content}"

        status_code, response_body, response_headers = send_email(
            SENDGRID_API_KEY, FROM_EMAIL, recipient, subject, reply_content
        )

        if status_code == 202:
            return HttpResponse("Reply sent successfully", status=202)
        else:
            return HttpResponse(response_body, status=status_code)
    return render(request, 'dashboard/reply_email.html')

@csrf_exempt
def add_domain(request):
    if request.method == 'POST':
        domain = request.POST.get('domain')
        url = "https://api.sendgrid.com/v3/whitelabel/domains"
        headers = {
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "domain": domain,
            "automatic_security": True
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            return JsonResponse({"message": "Domain added successfully", "data": response_data}, status=201)
        except requests.exceptions.RequestException as e:
            return HttpResponse(f"Failed to add domain: {str(e)}", status=500)
    return render(request, 'dashboard/add_domain.html')

@csrf_exempt
def verify_domain(request):
    if request.method == 'POST':
        domain_id = request.POST.get('domain_id')
        url = f"https://api.sendgrid.com/v3/whitelabel/domains/{domain_id}/validate"
        headers = {
            "Authorization": f"Bearer {SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return JsonResponse(response.json(), status=200)
        except requests.exceptions.RequestException as e:
            return HttpResponse(f"Failed to verify domain: {str(e)}", status=500)
    return render(request, 'dashboard/verify_domain.html')

def get_sent_emails(request):
    sent_emails = SentEmail.objects.all()
    return render(request, 'dashboard/sent_emails.html', {'sent_emails': sent_emails})

def get_received_emails(request):
    received_emails = ReceivedEmail.objects.all()
    return render(request, 'dashboard/received_emails.html', {'received_emails': received_emails})
