import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import EmailTemplate
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

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