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
                        "content": f"Summarize the following text to create a concise summary about the brand. The summary must include key details such as name, address, phone number, email, and unique selling points. It should get Email and Phone Number with country code but If any details are not found, provide '' or None. Format the summary in a list. Also, please Do not add any '*'(asterisks) at all in the output. For example: \n\nName: Scents N Stories\nAddress: Lahore\nPhone Number: +92 311 100 7862\nEmail: test@gmail.com\n\nUnique Selling Points: [Unique points about the brand]\n\nText to summarize: {combined_text}",
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
                    "content": f"Calculate the SEO score based on the following meta and slug information:\nMeta: {meta}\nSlug: {slug}, Just Provide me the Scores with headings, don't add any extra details or don't make it lengthy.Also, please Do not add any '*'(asterisks) at all in the output, give it in a list. For example:SEO Score:\nKeyword Usage (10/10)= 10\nMeta Description Length (5/10)= 5\nTitle Length (5/10)= 5\nMeta Count (8/10)= 8\nSlug Score (8/10)= 8\nTotal Score (36/50)= 36 ",
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
                    "content": f"Identify the technology stacks used by the website at the following URL: {url}. Provide the names of the technology stacks in the following format: Here are the technology stacks used by the website at the URL {url}: 1. Technology1 2. Technology2 3. Technology3 4. Technology4 5. Technology5 6. Technology6 7. Technology7",
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
                    "content": f"Provide a traffic analysis for the website at the following URL: {url}. Please provide me concise ad accurate traffic analysis,  don't add any extra details or don't make it lengthy.Also, please Do not add any '*'(asterisks) at all in the output.",
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
        'Name': r'Name:\s*(.*?)(?=\n|Phone Number|Email|Address|Unique Selling Points|$)',
        'Phone Number': r'Phone Number:\s*([+]?[\d\s()-\.]+)(?=\n|Name|Email|Address|Unique Selling Points|$)',
        'Email': r'Email:\s*(.*?)(?=\n|Name|Phone Number|Address|Unique Selling Points|$)',
        'Address': r'Address:\s*(.*?)(?=\n|Name|Phone Number|Email|Unique Selling Points|$)',
        'Unique Selling Points': r'Unique Selling Points:\s*((?:\*\s.*\n?)*)'
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


def parse_traffic_analysis(text):
    traffic_data = {
        'top_pages': {
            'labels': [],
            'data': []
        },
        'geographic_distribution': {
            'labels': [],
            'data': []
        }
    }

    print("Original text:", text)  # Debug print

    # Parsing Top Pages
    if "**Top Pages:**" in text:
        top_pages_section = text.split("**Top Pages:**")[1].split("**")[0].strip()
        print("Top Pages section found:", top_pages_section)  # Debug print
        top_pages_lines = top_pages_section.split('\n')
        for line in top_pages_lines:
            print(f"Processing Top Pages line: {line}")  # Debug print
            if ': ' in line and '% of total traffic' in line:
                page_name, traffic_percentage = line.split(': ')
                traffic_percentage = traffic_percentage.split('% of total traffic')[0]
                traffic_data['top_pages']['labels'].append(page_name.strip())
                traffic_data['top_pages']['data'].append(float(traffic_percentage.strip()))
            else:
                print(f"Top Pages parsing failed for line: {line}")

    else:
        print("Top Pages section not found")

    # Parsing Geographic Distribution
    if "**Geographic Distribution:**" in text:
        geo_distribution_section = text.split("**Geographic Distribution:**")[1].split("**")[0].strip()
        print("Geographic Distribution section found:", geo_distribution_section)  # Debug print
        geo_lines = geo_distribution_section.split('\n')
        for line in geo_lines:
            print(f"Processing Geographic Distribution line: {line}")  # Debug print
            if 'Top countries:' in line:
                countries = line.split('Top countries:')[1].strip().split(',')
                for country_info in countries:
                    if '(' in country_info and '%' in country_info:
                        country, percentage = country_info.split('(')
                        traffic_data['geographic_distribution']['labels'].append(country.strip())
                        traffic_data['geographic_distribution']['data'].append(float(percentage.split('%')[0].strip()))
                    else:
                        print(f"Country info parsing failed for line: {country_info}")
            elif 'Top cities:' in line:
                cities = line.split('Top cities:')[1].strip().split(',')
                for city_info in cities:
                    if '(' in city_info and '%' in city_info:
                        city, percentage = city_info.split('(')
                        traffic_data['geographic_distribution']['labels'].append(city.strip())
                        traffic_data['geographic_distribution']['data'].append(float(percentage.split('%')[0].strip()))
                    else:
                        print(f"City info parsing failed for line: {city_info}")
            else:
                print(f"Geographic Distribution parsing failed for line: {line}")

    else:
        print("Geographic Distribution section not found")

    return traffic_data
