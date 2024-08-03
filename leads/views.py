from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.core.serializers.json import DjangoJSONEncoder
from authentication.models import *
from django.db.models import Q
import json
import requests
from firecrawl import FirecrawlApp
import time
import os
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import re
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .utils import *
from dotenv import load_dotenv
load_dotenv()

google_api_key = os.getenv('GOOGLE_API_KEY')
search_engine_id = os.getenv('SEARCH_ENGINE_ID')
firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
builtwith_api_key = os.getenv('BUILTWITH_API_KEY')
backlink_api_key = os.getenv('BACKLINK_API_KEY')
similarweb_api_key = os.getenv('SIMILARWEB_API_KEY')
moz_access_id = os.getenv('MOZ_ACCESS_ID')
moz_secret_key = os.getenv('MOZ_SECRET_KEY')

def show_leads(request):
    leads = Lead.objects.filter(user_id=request.user)
    return render(request, 'dashboard/show_leads.html', {'leads': leads})

@login_required
@csrf_exempt
def add_lead(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        contact_no = request.POST.get('contact_no')
        industry = request.POST.get('industry')
        location = request.POST.get('location')
        notes = request.POST.get('notes')

        if not (name and contact_no and industry and location):
            return JsonResponse({'error': 'Invalid input'}, status=400)

        query = f'inurl: {name} {industry} {location}'
        url = f"https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={search_engine_id}&q={query}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            results = response.json()

            urls = results.get('items', [])
            most_relevant_link = urls[0]['link'] if urls else None
        except requests.RequestException as e:
            return JsonResponse({'error': f"Google Custom Search API error: {str(e)}"}, status=500)
        except ValueError:
            return JsonResponse({'error': 'Invalid JSON in Google Custom Search API response'}, status=500)
        except IndexError:
            return JsonResponse({'error': 'No relevant links found'}, status=404)

        if most_relevant_link:
            app = FirecrawlApp(api_key=firecrawl_api_key)
            retry_count = 0
            while retry_count < 5:
                try:
                    r = requests.get(most_relevant_link)
                    html_content = r.text
                    scraped_data = app.scrape_url(most_relevant_link)
                    if scraped_data and 'content' in scraped_data and scraped_data['content']:
                        content = scraped_data['content']
                        result = process_website_content(most_relevant_link, content, html_content)

                        # Parse brand summary
                        parsed_summary = parse_brand_summary(result['brand_summary'])

                        # Create a new Lead associated with the logged-in user
                    if parsed_summary['Email'] and parsed_summary['Phone Number']:
                        lead = Lead.objects.create(
                            user=request.user,
                            link=most_relevant_link,
                            brand_summary=result['brand_summary'].strip(),
                            seo_score=result['seo_score'],
                            tech_stacks='\n'.join(result['tech_stacks']),  # Convert list to newline-separated string
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

                        success_message = "Lead added successfully"
                        return JsonResponse({'status': 'Lead added', 'success_message': success_message})
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

    return render(request, 'dashboard/add_lead.html')


@csrf_exempt
def find_leads(request):
    query = request.GET.get('query', '')
    
    leads = Lead.objects.filter(
        Q(industry__icontains=query) |
        Q(location__icontains=query) |
        Q(name__icontains=query) |
        Q(contact_no=query),
        user=request.user
    )

    leads_data = [{
        'id': lead.id,
        'name': lead.name,
        'contact_no': lead.contact_no,
        'industry': lead.industry,
        'location': lead.location,
        'notes': lead.notes
    } for lead in leads]
    
    return render(request, 'dashboard/find_leads.html', {'leads': leads_data})


@csrf_exempt
def add_notes(request, id):
    try:
        lead = Lead.objects.get(id=id)
        if request.method == 'POST':
            notes = request.POST.get('notes')
            if notes:
                lead.notes = lead.notes + '\n' + notes if lead.notes else notes
                lead.save()
                return JsonResponse({'id': lead.id, 'status': 'Notes added'})
            return JsonResponse({'error': 'No notes provided'}, status=400)
        return HttpResponse(status=405)
    except Lead.DoesNotExist:
        return JsonResponse({'error': 'Lead not found'}, status=404)


@csrf_exempt
@login_required
def generate_shopifystoresdetail(request):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
        industry = user_profile.industry
        location = user_profile.location
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User profile not found'}, status=404)

    if not (industry and location):
        return JsonResponse({'error': 'Industry and location parameters are required'}, status=400)

    query = f'inurl:myshopify.com {industry} {location}'
    url = f"https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={search_engine_id}&q={query}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        results = response.json()
    except requests.RequestException as e:
        return JsonResponse({'error': f"Google Custom Search API error: {str(e)}"}, status=500)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON in Google Custom Search API response'}, status=500)

    final_links = []
    email_contents = []

    if not firecrawl_api_key:
        return JsonResponse({'error': 'Firecrawl API key is not set'}, status=500)

    app = FirecrawlApp(api_key=firecrawl_api_key)

    for item in results.get('items', []):
        final_links.append(item['link'])

        retry_count = 0
        while retry_count < 5:
            try:
                r = requests.get(item['link'])
                url_html_content = r.text
                scraped_data = app.scrape_url(item['link'])
                if scraped_data and 'content' in scraped_data and scraped_data['content']:
                    content = scraped_data['content']
                    brand_summary = summarize_text(content)
                    # Extract meta and slug from HTML content
                    meta, slug = extract_meta_and_slug(url_html_content)
                    # Score the website for SEO
                    seo_score = calculate_seo_score(meta, slug)
                    # Get backlinks, tech stacks, and traffic analysis
                    # backlinks = get_backlinks(item['link'])
                    tech_stacks = get_tech_stacks(item['link'])
                    traffic_analysis = get_traffic_analysis(item['link'])
                    parsed_summary = parse_brand_summary(brand_summary)

                    Lead.objects.create(
                        user=request.user,
                        link=item['link'],
                        brand_summary=brand_summary.strip(),
                        seo_score=seo_score,
                        tech_stacks="\n".join(tech_stacks),  # Convert list to newline-separated string
                        traffic_analysis=traffic_analysis,
                        name=parsed_summary['Name'],
                        contact_no=parsed_summary['Phone Number'],
                        industry=industry,
                        location=location,
                        email=parsed_summary['Email'],
                        address=parsed_summary['Address'],
                        phone_number=parsed_summary['Phone Number']
                    )

                    email_subject = f"Exploring Collaboration Opportunities with {item['link']}"
                    email_body_html = render_to_string('email_template.html', {
                        'item_link': item['link'],
                        'brand_summary': brand_summary.strip(),
                        'seo_score': seo_score,
                        # 'backlinks': backlinks,
                        'tech_stacks': tech_stacks,
                        'traffic_analysis': traffic_analysis
                    })
                    email_body_text = strip_tags(email_body_html)

                    email_contents.append({
                        "link": item['link'],
                        "summary": brand_summary.strip(),
                    })
                else: 
                    email_contents.append({
                        "link": item['link'],
                        "summary": "No content available",
                    })

                break
            except requests.RequestException as e:
                if 'rate limit exceeded' in str(e).lower():
                    retry_count += 1
                    wait_time = 2 ** retry_count
                    time.sleep(wait_time)
                else:
                    print(f"Error processing {item['link']}: {str(e)}")
                    email_contents.append({
                        "link": item['link'],
                        "summary": f"Error: {str(e)}",
                    })
                    break
            except Exception as e:
                print(f"Unexpected error processing {item['link']}: {str(e)}")
                email_contents.append({
                    "link": item['link'],
                    "summary": f"Error: {str(e)}",
                })
                break
    leads = Lead.objects.all()

    # Prepare data for charts and tables
    lead_data = []

    for lead in leads:
        # Split the string by newlines
        lines = lead.tech_stacks.strip().split('\n')

        # Skip the first line and any potential empty lines
        tech_stacks_raw = [line.strip() for line in lines[1:] if line.strip()]

        # Remove numbering (optional)
        tech_stacks = [line.split('. ', 1)[-1] for line in tech_stacks_raw]
        print(tech_stacks)

        lead_data.append({
            'name': lead.name,
            'link': lead.link,
            'brand_summary': lead.brand_summary,
            'seo_score': lead.seo_score,
            'tech_stacks': tech_stacks,
            'traffic_analysis': lead.traffic_analysis
        })
    print(lead_data)
    return render(request, 'dashboard/leads_success.html', {'leads': lead_data})


@csrf_exempt
@login_required
def lead_detail(request, lead_id):
    lead = get_object_or_404(Lead, pk=lead_id)
    tech_stacks_list = lead.get_tech_stacks_list()
    labels, data = lead.get_seo_scores()

    # Parse traffic analysis
    traffic_data = parse_traffic_analysis(lead.traffic_analysis) if lead.traffic_analysis else {}
    traffic_analysis_json = json.dumps(traffic_data, cls=DjangoJSONEncoder)
    print(traffic_analysis_json)  # Debug print

    context = {
        'lead': lead,
        'seo_labels': json.dumps(labels, cls=DjangoJSONEncoder),
        'tech_stacks_list': tech_stacks_list,
        'seo_data': json.dumps(data, cls=DjangoJSONEncoder),
        'traffic_analysis': traffic_analysis_json
    }
    return render(request, 'dashboard/lead_detail.html', context)