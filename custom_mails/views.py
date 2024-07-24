from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import SentEmail, ReceivedEmail
from django.views.decorators.csrf import csrf_exempt
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from django.urls import reverse
import logging
import requests
from django.template.loader import render_to_string
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

SENDGRID_API_BASE_URL = "https://api.sendgrid.com/v3"
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

        if recipient:
         recipient_name = extract_name_from_email(recipient)

        if status_code == 202:
            # Assuming you have a SentEmail model defined
            SentEmail.objects.create(
                recipient=recipient,
                subject=subject,
                html_body=html_body,
                recipient_name=recipient_name,
            )
            return HttpResponse("Email sent successfully", status=202)
        else:
            return HttpResponse(response_body, status=status_code)
    return render(request, 'dashboard/send_mail.html')


def extract_name_from_email(email):
    name_part = email.split('@')[0]
    # Optionally replace dots or underscores with spaces and capitalize
    name = name_part.replace('.', ' ').replace('_', ' ').title()
    return name


@csrf_exempt
def receive_mail(request):
    if request.method == 'POST':
        sender = request.POST.get('sender')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        if sender:
         sender_name = extract_name_from_email(sender)
        

        
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
            content=content,
            sender_name = sender_name
        )

        return HttpResponse(html_content)

    return render(request, 'dashboard/receive_mail.html')

def reply_email(request, email_id):
    original_email = get_object_or_404(ReceivedEmail, id=email_id)
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        html_body = request.POST.get('html_body')
        recipient = original_email.sender

        status_code, response_body, response_headers = send_email(
            SENDGRID_API_KEY, FROM_EMAIL, recipient, subject, html_body
        )
        if recipient:
         recipient_name = extract_name_from_email(recipient)

        if status_code == 202:
        # Save the replied email in SentEmail model
            reply_email = SentEmail.objects.create(
                subject=subject,
                html_body=html_body,
                recipient=recipient,
                recipient_name=recipient_name
                
            )
            return HttpResponse("Email sent successfully", status=202)
        
    context = {
        'original_email': original_email,
        'reply_subject': f"Re: {original_email.subject}",
    }
    return render(request, 'dashboard/reply_email.html', context)

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
    total_emails = SentEmail.objects.count()
    return render(request, 'dashboard/sent_emails.html', {'sent_emails': sent_emails, 'total_emails': total_emails})

def get_received_emails(request):
    received_emails = ReceivedEmail.objects.all()
    total_emails = ReceivedEmail.objects.count()
    return render(request, 'dashboard/received_emails.html', {'received_emails': received_emails, 'total_emails': total_emails})


def configure_inbound_parse_settings(domain, url):
    parse_url = f"{SENDGRID_API_BASE_URL}/user/webhooks/parse/settings"
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "hostname": domain,
        "url": url,
        "spam_check": True,  # Set based on your preference
        "send_raw": False,  # Set based on your preference
        "inbound_security": []  # Add any inbound security settings if required
    }
    response = requests.post(parse_url, headers=headers, json=payload)
    return response.json()

@csrf_exempt
def configure_receive_endpoint_view(request):
    if request.method == 'POST':
        try:
            domain = request.POST.get('domain')
            endpoint_url = request.POST.get('endpoint_url')
            
            if not (domain and endpoint_url):
                return render(request, 'configure_receive_endpoint.html', {
                    'error': 'Domain and endpoint URL are required.'
                })

            result = configure_inbound_parse_settings(domain, endpoint_url)
            print(result)
            return render(request, 'dashboard/configure_receive_endpoint.html', {
                'message': 'Inbound parse configuration result.',
                'result': result
            })
        
        except Exception as e:
            logger.error("Error in configure_receive_endpoint_view: %s", str(e))
            return render(request, 'dashboard/configure_receive_endpoint.html', {
                'error': str(e)
            })
    else:
        return render(request, 'dashboard/configure_receive_endpoint.html')
    
def read_email(request, email_id):
    email = get_object_or_404(ReceivedEmail, id=email_id)
    return render(request, 'dashboard/read_email.html', {'email': email})


def read_sent_email(request, email_id):
    email = get_object_or_404(SentEmail, id=email_id)
    return render(request, 'dashboard/read_sent_mail.html', {'email': email})





def reply_sent_email(request, email_id):
    original_email = get_object_or_404(SentEmail, id=email_id)
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        html_body = request.POST.get('html_body')
        recipient = original_email.recipient

        status_code, response_body, response_headers = send_email(
            SENDGRID_API_KEY, FROM_EMAIL, recipient, subject, html_body
        )
        if recipient:
         sender_name = extract_name_from_email(recipient)
        if status_code == 202:
        # Save the replied email in SentEmail model
            reply_email = SentEmail.objects.create(
                subject=subject,
                html_body=html_body,
                recipient=recipient,
                
            )
            return HttpResponse("Email sent successfully", status=202)
        
    context = {
        'original_email': original_email,
        'reply_subject': f"Re: {original_email.subject}",
    }
    return render(request, 'dashboard/reply_sent_mail.html', context)