from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json, requests, os
from firecrawl import FirecrawlApp
from demo_techrealm.models import Lead
from demo_techrealm.utils import (
    process_website_content, 
    parse_brand_summary, 
    parse_traffic_analysis, 
    format_brand_summary, 
    extract_technology_stacks
)
from django.core.serializers.json import DjangoJSONEncoder
from dotenv import load_dotenv
load_dotenv()

google_api_key = os.getenv('GOOGLE_API_KEY')
search_engine_id = os.getenv('SEARCH_ENGINE_ID')
firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')

def index(request):
    lead = Lead.objects.last()

    # Handle the case where lead might be None
    if lead:
        formatted_summary = format_brand_summary(lead.brand_summary) if lead.brand_summary else 'No summary available'
        tech_stacks_list = extract_technology_stacks(lead.tech_stacks) if lead.tech_stacks else []
        labels, data = lead.get_seo_scores() if lead.get_seo_scores() else ([], [])
        traffic_data = parse_traffic_analysis(lead.traffic_analysis) if lead.traffic_analysis else {}
    else:
        formatted_summary = 'No summary available'
        tech_stacks_list = []
        labels, data = [], []
        traffic_data = {}

    traffic_analysis_json = json.dumps(traffic_data, cls=DjangoJSONEncoder)

    context = {
        'lead': lead,
        'formatted_summary': formatted_summary,
        'tech_stacks_list': tech_stacks_list,
        'traffic_analysis': traffic_analysis_json,
        'seo_data': json.dumps(data, cls=DjangoJSONEncoder),
        'seo_labels': json.dumps(labels, cls=DjangoJSONEncoder),
    }

    return render(request, 'demo_techrealm/landing.html', context)

@csrf_exempt
def add_lead(request):
    if request.method == 'POST':
        print(request.POST.get('name'), request.POST.get('industry'), request.POST.get('location'))
        name = request.POST.get('name')
        contact_no = request.POST.get('contact_no')
        industry = request.POST.get('industry')
        location = request.POST.get('location')
        notes = request.POST.get('notes')

        # Validate required fields
        if not (name and contact_no and industry and location):
            return JsonResponse({'error': 'Invalid input'}, status=400)

        # Google Custom Search API
        query = f'inurl: {name} {industry} {location}'
        url = f"https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={search_engine_id}&q={query}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            results = response.json()
            urls = results.get('items', [])
            most_relevant_link = urls[0]['link'] if urls else None
            print(most_relevant_link)
        except requests.RequestException as e:
            return JsonResponse({'error': f"Google Custom Search API error: {str(e)}"}, status=500)
        except ValueError:
            return JsonResponse({'error': 'Invalid JSON in Google Custom Search API response'}, status=500)
        except IndexError:
            return JsonResponse({'error': 'No relevant links found'}, status=404)

        # If a relevant link is found
        if most_relevant_link:
            app = FirecrawlApp(api_key=firecrawl_api_key)
            retry_count = 0
            while retry_count < 5:
                try:
                    r = requests.get(most_relevant_link)
                    html_content = r.text
                    print('html_content= ',html_content)
                    scraped_data = app.scrape_url(most_relevant_link)
                    print('scraped_data= ',scraped_data)
                    if scraped_data and 'content' in scraped_data and scraped_data['content']:
                        content = scraped_data['content']
                        result = process_website_content(most_relevant_link, content, html_content)
                        print(result['brand_summary'])
                        # Parse brand summary
                        parsed_summary = parse_brand_summary(result['brand_summary'])

                        # Create a new Lead if email and phone number are present
                        if parsed_summary['Email'] and parsed_summary['Phone Number']:
                            try:
                                print('lead is being created')
                                lead = Lead.objects.create(
                                    link=most_relevant_link,
                                    brand_summary=result['brand_summary'].strip(),
                                    seo_score=result['seo_score'],
                                    tech_stacks='\n'.join(result['tech_stacks']),
                                    traffic_analysis=result['traffic_analysis'],
                                    name=parsed_summary['Name'] or name,
                                    contact_no=contact_no,
                                    industry=industry,
                                    location=location,
                                    notes=notes,
                                    email=parsed_summary['Email'],
                                    address=parsed_summary['Address'],
                                    phone_number=parsed_summary['Phone Number']
                                )
                                print('Lead added successfully')
                                return JsonResponse({'status': 'success'})
                            except Exception as e:
                                print(f'Error creating Lead: {str(e)}')
                                return JsonResponse({'error': f"Error creating Lead: {str(e)}"}, status=500)
                        else:
                            error_message = "Lead has no "
                            if not parsed_summary['Email']:
                                error_message += "email"
                            if not parsed_summary['Email'] and not parsed_summary['Phone Number']:
                                error_message += " or "
                            if not parsed_summary['Phone Number']:
                                error_message += "phone number"
                            return JsonResponse({'status': 'error', 'error_message': error_message})
                except Exception as e:
                    retry_count += 1
                    if retry_count == 5:
                        return JsonResponse({'error': f"Failed to scrape the URL after multiple attempts: {str(e)}"}, status=500)
        else:
            return JsonResponse({'error': 'No relevant link found'}, status=404)

    return render(request, 'demo_techrealm/landing.html')


def lead_iframe(request):
    return render(request, 'demo_techrealm/iframe.html')