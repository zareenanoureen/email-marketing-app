# AI Email Marketing App Documentation

**Developed by:** Zareena Noureen  
**App URL:** https://mailingai.techrealm.pk/  

---

## Overview

The AI Email Marketing App is designed to enhance email marketing strategies for businesses by providing a user-friendly interface, data-driven insights, and AI-driven automation. The app is tailored for businesses looking to optimize their outreach and improve lead generation through customized email campaigns.

### Key Features:
- Lead management and generation
- Mail management (compose, inbox, and sent mail)
- AI-driven campaign optimization
- Analytics for leads and campaigns

---

## User Interface

### Visual Design:
- **Visual Hierarchy:** Elements are organized to guide user attention effectively, improving navigation and reducing cognitive load.
- **Color Scheme:** A cohesive color palette is used for readability and accessibility.
- **Interactive Elements:** Responsive buttons and engaging icons enhance the user experience.

---

## Technology Stack

- **Programming Languages:** JavaScript, Python
- **Framework:** Django for backend development
- **Development Tools:** Git for version control, Docker for containerization

---

## User Authentication

### Sign In & Sign Up:
- Users can log in with their email and password. New users can create an account by providing email, username, phone number, and a secure password.

---

## Getting Started

When a new user signs in, they must provide their business details, including:
- Business description
- Industry name
- Target location

These inputs help personalize lead generation and marketing strategies.

---

## Dashboard Overview

The dashboard serves as the central hub for managing leads and email campaigns. It contains three main modules:
1. **Leads Management**
2. **Mail Management**
3. **AI Optimization**

Users can log out from the button located in the top right corner.

---

## Leads Management

### Key Functionalities:
- **Generate Leads:** Users can generate and view leads relevant to their business needs. A notification informs the user while the leads are being generated.
- **View Leads:** Once generated, leads can be viewed with detailed information.
- **Add Leads:** Users can manually add leads by specifying brand name, location, industry, and notes.
- **Find Leads:** This feature allows users to search for specific leads.

### Lead Analytics:
- Detailed analytics on each lead include brand name, website link, and SEO scores. Visual tools like pie charts and line graphs display performance metrics.

---

## Mail Management

This module handles email communication. Two main tabs include:

1. **Domain Configuration**
   - Add, verify, and configure domains to enable email sending and receiving.
   - Domain verification improves email deliverability.
   
2. **Mail Management**
   - Users can compose emails, view their inbox, and read sent emails.
   - Features include replying to emails and tracking sent mail status.

---

## AI Optimization

The AI-driven functionality automates email campaigns by selecting targeted leads and providing personalized email templates. Campaigns can be monitored to track engagement and performance.

---

## Campaign Creation

### Process:
- Users can select leads, define product or service details, and create personalized email campaigns. Post-campaign, they can track engagement and analyze responses for future optimization.

---

## User Benefits

- **Streamlined Processes:** Automating the email marketing workflow reduces manual effort, allowing users to focus on strategy.
- **Efficient Lead Generation:** Optimized lead generation provides relevant prospects.
- **Enhanced Engagement:** AI functionalities enable personalized email content, improving user engagement rates.

---

## Contact & Support

For any issues or further assistance, visit [AI Email Marketing App](https://mailingai.techrealm.pk/) or contact the development team:

**Developer:** Zareena Noureen  
**Developer Email:** [zareena.bintenafees@gmail.com](mailto:zareena.bintenafees@gmail.com)

---


## Folder Structure

- `.env`
- `.github-ci.yml`
- `.gitignore`
- `db.sqlite3`
- `docker-compose.yml`
- `Dockerfile`
- `docs.md`
- `manage.py`
- `README.md`
- `requirement.txt`
- `requirements.txt`
- `setup.md`

## .github/
- workflows/
  - `backend.yml`

## ai_optimization/
- `__init__.py`
- `admin.py`
- `apps.py`
- `models.py`
- `tests.py`
- `urls.py`
- `utils.py`
- `views.py`

## authentication/
- `__init__.py`
- `admin.py`
- `apps.py`
- `models.py`
- `tests.py`
- `urls.py`
- `utils.py`
- `views.py`
- static/
- templates/

## custom_mails/
- `__init__.py`
- `admin.py`
- `apps.py`
- `models.py`
- `tests.py`
- `urls.py`
- `views.py`

## demo_techrealm/
- `__init__.py`
- `admin.py`
- `apps.py`
- `models.py`
- `tests.py`
- `urls.py`
- `utils.py`
- `views.py`
- templates/

## leads/
- `__init__.py`
- `admin.py`
- `apps.py`
- `models.py`
- `tests.py`
- `urls.py`
- `utils.py`
- `views.py`
- templates/
  - `email_template.html`

## LeadsManagement/
- `__init__.py`
- `asgi.py`
- `settings.py`
- `urls.py`
- `wsgi.py`

## static/
- admin/
- authentication/
- media_demo/
- rest_framework/

## staticfiles/
- admin/
- authentication/
- media_demo/
- rest_framework/