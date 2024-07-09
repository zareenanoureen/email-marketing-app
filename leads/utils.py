import os, re
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

groq_api_key  = os.getenv('GROQ_API_KEY')

client = Groq(api_key=groq_api_key)
model = "llama3-8b-8192"

def summarize_text(text, chunk_size=500):
    summary = ""
    
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        combined_text = summary + " " + chunk
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize the following text to create a concise summary about the brand, must include key details such as name, address, phone number, and unique selling points: {combined_text}",
                    }
                ],
                model="llama3-8b-8192",
            )
            summary = chat_completion.choices[0].message.content.strip()
        except Exception as e:
            summary = f"Error in summarization: {str(e)}"
            break  # Exit the loop on error to avoid further calls with the same issue
    
    return summary

# Helper function to calculate SEO score using Groq API
def calculate_seo_score(meta, slug):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Calculate the SEO score based on the following meta and slug information:\nMeta: {meta}\nSlug: {slug}",
                }
            ],
            model=model,
        )
        seo_score = chat_completion.choices[0].message.content.strip()
    except Exception as e:
        seo_score = f"Error in SEO score calculation: {str(e)}"
    
    return seo_score

# Helper function to get technology stacks using Groq API
def get_tech_stacks(url):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Identify the technology stacks used by the website at the following URL: {url}",
                }
            ],
            model=model,
        )
        tech_stacks = chat_completion.choices[0].message.content.strip().split('\n')
    except Exception as e:
        tech_stacks = [f"Error in fetching technology stacks: {str(e)}"]
    
    return tech_stacks

# Helper function to get traffic analysis using Groq API
def get_traffic_analysis(url):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Provide a traffic analysis for the website at the following URL: {url}",
                }
            ],
            model=model,
        )
        traffic_analysis = chat_completion.choices[0].message.content.strip()
    except Exception as e:
        traffic_analysis = f"Error in fetching traffic analysis: {str(e)}"
    
    return traffic_analysis

# Helper function to extract meta and slug from HTML
def extract_meta_and_slug(html_content):
    # Extract meta description
    meta_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
    meta = meta_match.group(1) if meta_match else 'No meta description available'
    
    # Extract slug
    slug_match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
    slug = slug_match.group(1).split('/')[-1] if slug_match else 'No slug available'
    
    return meta, slug

