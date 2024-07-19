import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
from .utils import *
from leads.models import *
from groq import Groq
from django.shortcuts import render, get_object_or_404
from custom_mails.views import send_email
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
load_dotenv()

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
FROM_EMAIL = 'info@learnity.store'

groq_api_key  = os.getenv('GROQ_API_KEY')
client = Groq(api_key=groq_api_key)
model = "llama3-8b-8192"

def generate_email_template(request):
    if request.method == 'POST':
        # Define the prompt for generating the email template
        prompt = """
        Generate an email template in HTML for a marketing campaign. The email should showcase our latest products, provide a brief description. Make sure the template is visually appealing and follows best practices for email marketing.
        """

        # Generate the template using the Groq API
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                n=1,
                stop=None,
                temperature=0.7
            )
            template_content = response.choices[0].message.content.strip()

            # Save the generated template to the database
            email_template = EmailTemplate(content=template_content)
            email_template.save()

            return JsonResponse({'status': 'success', 'message': 'Template generated and saved successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, 'dashboard/generate_email_template.html')

def view_template(request):
    try:
        email_template = EmailTemplate.objects.latest('created_at')
        return render(request, 'dashboard/view_template.html', {'template_content': email_template})
    except EmailTemplate.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'No template found.'})
    
@csrf_exempt
def create_campaign(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        no_of_target_leads = int(request.POST.get('no_of_target_leads'))
        products = request.POST.get('products')
        my_brand = request.POST.get('my_brand')

        # Create the campaign
        campaign = Campaign.objects.create(
            name=name,
            no_of_target_leads=no_of_target_leads,
            products=products,
            my_brand=my_brand
        )

        # Fetch the first email template
        email_template = EmailTemplate.objects.first()
        if not email_template:
            return HttpResponse("No email template found", status=404)
        base_template = email_template.body

        # Fetch the required leads
        leads = Lead.objects.filter(
            phone_number__isnull=False, 
            email__isnull=False
        ).exclude(
            phone_number='', 
            email=''
        )[:no_of_target_leads]

        if not leads:
            return HttpResponse("No leads found", status=404)

        generated_emails = []
        for lead in leads:
            # Generate the email content using the Groq API
            subject, customized_email_body = generate_email_templates(campaign, lead, base_template)

            # Send the email
            try:
                send_email(
                SENDGRID_API_KEY, FROM_EMAIL, lead.email, subject, customized_email_body
                )
            except Exception as e:
                return HttpResponse(f"Error sending email: {str(e)}", status=500)

            # Save the generated email to the database
            ai_sent_mail = AISentMails(
                campaign=campaign,
                subject=subject,
                body=customized_email_body
            )
            generated_emails.append(ai_sent_mail)

        # Bulk create AISentMails for efficiency
        AISentMails.objects.bulk_create(generated_emails)

        return render(request, 'dashboard/campaign_success.html', {'generated_emails': generated_emails})

    return render(request, 'dashboard/create_campaign.html')

def campaign_list(request):
    campaigns = Campaign.objects.all()
    return render(request, 'dashboard/campaign_list.html', {'campaigns': campaigns})

def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    sent_mails = AISentMails.objects.filter(campaign=campaign)
    return render(request, 'dashboard/campaign_detail.html', {'campaign': campaign, 'sent_mails': sent_mails})

def sent_mail_detail(request, mail_id):
    sent_mail = get_object_or_404(AISentMails, pk=mail_id)
    return render(request, 'dashboard/sent_mail_detail.html', {'sent_mail': sent_mail})

def respond_email(request, mail_id):
    if request.method == 'POST':
        response = request.POST.get('response')
        sent_mail = get_object_or_404(AISentMails, pk=mail_id)

        # Send the response email
        send_email(
            subject=f"Response to: {sent_mail.subject}",
            message=response,
            from_email=FROM_EMAIL,
            recipient_list=sent_mail.lead.email,  # Adjust to match your lead email field
        )

        # Redirect to a success page or back to the mail detail page
        return redirect('sent_mail_detail', mail_id=mail_id)

    return redirect('sent_mail_detail', mail_id=mail_id)