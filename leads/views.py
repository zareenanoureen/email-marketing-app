from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import *
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
    leads = ShopifyStoresDetails.objects.all()
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

        query = f'inurl:myshopify.com {name} {industry} {location}'
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
                    scraped_data = app.scrape_url(most_relevant_link)
                    if scraped_data and 'content' in scraped_data and scraped_data['content']:
                        content = scraped_data['content']
                        brand_summary, seo_score, tech_stacks, traffic_analysis = process_website_content(most_relevant_link, content)

                        # Create a new Lead associated with the logged-in user
                        lead = Lead.objects.create(
                            user=request.user,
                            name=name,
                            contact_no=contact_no,
                            industry=industry,
                            location=location,
                            notes=notes
                        )

                        # Create ShopifyStoresDetails associated with the created Lead
                        ShopifyStoresDetails.objects.create(
                            lead=lead,
                            link=most_relevant_link,
                            brand_summary=brand_summary.strip(),
                            seo_score=seo_score,
                            tech_stacks='\n'.join(tech_stacks),  # Convert list to newline-separated string
                            traffic_analysis=traffic_analysis
                        )

                        success_message = "Lead added successfully"
                        return render(request, 'dashboard/add_lead.html', {'name': name, 'status': 'Lead added', 'success_message': success_message})
                except Exception as e:
                    retry_count += 1
                    if retry_count == 5:
                        return JsonResponse({'error': f"Failed to scrape the URL after multiple attempts: {str(e)}"}, status=500)
        else:
            return JsonResponse({'error': 'No relevant link found'}, status=404)

    return render(request, 'dashboard/add_lead.html')

@csrf_exempt
def get_or_update_lead(request, id):
    try:
        lead = Lead.objects.get(id=id)
        
        if request.method == 'PUT':
            data = json.loads(request.body)
            name = data.get('name')
            contact_no = data.get('contact_no')
            industry = data.get('industry')
            location = data.get('location')
            notes = data.get('notes')
            address = data.get('address')

            if name:
                lead.name = name
            if contact_no:
                lead.contact_no = contact_no
            if industry:
                lead.industry = industry
            if location:
                lead.location = location
            if notes:
                lead.notes = notes
            if address:
                lead.address = address

            lead.save()
            return JsonResponse({'id': lead.id, 'name': lead.name, 'industry': lead.industry, 'contact_no': lead.contact_no, 'location': lead.location, 'address': lead.address, 'status': 'Lead updated'})

        elif request.method == 'GET':
            # Handle GET request to retrieve lead details
            lead_data = {
                'id': lead.id,
                'name': lead.name,
                'contact_no': lead.contact_no,
                'industry': lead.industry,
                'location': lead.location,
                'notes': lead.notes,
                'address': lead.address
            }
            return JsonResponse(lead_data)

        else:
            return HttpResponse(status=405)  # Method Not Allowed for other methods
    
    except Lead.DoesNotExist:
        return JsonResponse({'error': 'Lead not found'}, status=404)

@csrf_exempt
def find_leads(request):
    query = request.GET.get('query', '')
    
    leads = Lead.objects.filter(
        Q(industry__icontains=query) |
        Q(location__icontains=query) |
        Q(name__icontains=query) |
        Q(contact_no=query)
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
                scraped_data = app.scrape_url(item['link'])
                if scraped_data and 'content' in scraped_data and scraped_data['content']:
                    content = scraped_data['content']
                    brand_summary = summarize_text(content)
                    # Extract meta and slug from HTML content
                    meta, slug = extract_meta_and_slug(content)
                    # Score the website for SEO
                    seo_score = calculate_seo_score(meta, slug)
                    # Get backlinks, tech stacks, and traffic analysis
                    # backlinks = get_backlinks(item['link'])
                    tech_stacks = get_tech_stacks(item['link'])
                    traffic_analysis = get_traffic_analysis(item['link'])

                    ShopifyStoresDetails.objects.create(
                        link=item['link'],
                        brand_summary=brand_summary.strip(),
                        seo_score=seo_score,
                        # backlinks=backlinks,
                        tech_stacks=tech_stacks,
                        traffic_analysis=traffic_analysis
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
    leads = ShopifyStoresDetails.objects.all()

    # Prepare data for charts and tables
    lead_data = []
    for lead in leads:
        lead_data.append({
            'link': lead.link,
            'brand_summary': lead.brand_summary,
            'seo_score': lead.seo_score,
            'tech_stacks': lead.tech_stacks,
            'traffic_analysis': lead.traffic_analysis
        })

    return render(request, 'dashboard/all_leads.html', {'leads': lead_data})