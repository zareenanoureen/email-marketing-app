import os, re
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

groq_api_key  = os.getenv('GROQ_API_KEY')

client = Groq(api_key=groq_api_key)
model = "llama3-8b-8192"

def summarize_text(text, chunk_size=1000):
    summary = ""
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        combined_text = summary + " " + chunk     
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize the following text to create a concise summary about the brand. The summary must include key details such as name, address, phone number, email, and unique selling points. It should get Email and Phone Number with country code but If any details are not found, provide '' or None. Format the summary in a list. For example: \n\nName: Scents N Stories\nAddress: Lahore\nPhone Number: +92 311 100 7862\nEmail: test@gmail.com\n\nUnique Selling Points: [Unique points about the brand]\n\nText to summarize: {combined_text}",
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
                    "content": f"Calculate the SEO score based on the following meta and slug information:\nMeta: {meta}\nSlug: {slug}, Just Provide me the Scores with headings",
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
                    "content": f"Identify the technology stacks used by the website at the following URL: {url}, Just give me the names of Technology stacks.",
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
                    "content": f"Provide a traffic analysis for the website at the following URL: {url}. Please provide me concise ad accurate traffic analysis",
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

from bs4 import BeautifulSoup


def extract_meta_and_slug_soup(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extract meta description
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    if meta_tag:
        meta = meta_tag['content']
    else:
        meta = 'No meta description available'
        print("Meta tag not found")

    # Extract slug
    canonical_link = soup.find('link', rel='canonical')
    if canonical_link:
        slug = canonical_link['href'].split('/')[-1]
    else:
        slug = 'No slug available'
        print("Canonical link not found")
    
    return meta, slug

def process_website_content(url, markdown_content, html_content):
    meta, slug = extract_meta_and_slug_soup(html_content)
    brand_summary = summarize_text(markdown_content)
    tech_stacks = get_tech_stacks(url)
    seo_score = calculate_seo_score(meta, slug)
    traffic_analysis = get_traffic_analysis(url)
    
    return {
        "brand_summary": brand_summary,
        "seo_score": seo_score,
        "tech_stacks": tech_stacks,
        "traffic_analysis": traffic_analysis
    }


def parse_brand_summary(summary):
    # Define patterns for extracting key-value pairs
    patterns = {
        'Name': r'\*\*Name:\*\*\s*(.*?)\n',
        'Phone Number': r'\*\*Phone Number:\*\*\s*([+]?[\d\s()-\.]+)',
        'Email': r'\*\*Email:\*\*\s*(.*?)\n',
        'Address': r'\*\*Address:\*\*\s*(.*?)\n',
        'Unique Selling Points': r'\*\*Unique Selling Points:\*\*\s*((?:\*\s.*\n?)*)'
    }

    # Initialize variables to store extracted values
    extracted_values = {
        'Name': None,
        'Phone Number': None,
        'Email': None,
        'Address': None,
        'Unique Selling Points': None
    }

    # Extract values using regex patterns
    for key, pattern in patterns.items():
        match = re.search(pattern, summary, re.IGNORECASE)
        if match:
            extracted_values[key] = match.group(1).strip()

    return extracted_values