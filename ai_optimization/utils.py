import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

groq_api_key  = os.getenv('GROQ_API_KEY')
client = Groq(api_key=groq_api_key)
model = "llama3-8b-8192"

def generate_email_templates(campaign, lead, base_template):
    prompt = f"""
    Generate an email template for a marketing campaign. The email should showcase the following products: {campaign.products} that we offering to leads. Provide a brief description of each product/service and ensure the template is visually appealing and follows best practices for email marketing. The email should address the lead by name ({lead.name}) and mention their main points like brand summary ({lead.brand_summary}), seo score ({lead.seo_score}), traffic analysis ({lead.traffic_analysis}) and some other details . It should also include our brand name ({campaign.my_brand}) and reference the lead's website ({lead.name}). You should use Base template for inclusion of this data.
    Base template: {base_template}
    Don't add extra details like: 

    P.S. Feel free to reach out to me if you have any questions or would like to schedule a call.

    You can adjust the template as per your requirements and branding. Make sure to customize the email by replacing the placeholders with the actual data.

    Also remove this: [Your Name]
    Just the brand Name below.

    Just provide me the Generated Subject and Body.
    """

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
        if template_content.startswith("Here is the generated email template:"):
            template_content = template_content[len("Here is the generated email template:"):].strip()

        # Extract subject and body
        subject_start = template_content.find("**Subject:**") + len("**Subject:**")
        subject_end = template_content.find("**Body:**")
        subject = template_content[subject_start:subject_end].strip()

        body_start = subject_end + len("**Body:**")
        body = template_content[body_start:].strip()
        return subject, body
    except Exception as e:
        return f"Error generating email template: {str(e)}"