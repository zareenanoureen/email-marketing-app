# Django Project

## Installation

Follow these steps to set up the Django project on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.x**: You can download it from [here](https://www.python.org/downloads/).
- **Pip**: Python’s package manager. It usually comes with Python, but you can install it separately if needed.
- **Virtualenv** (optional but recommended): To keep dependencies isolated for this project.

### Step-by-Step Installation

1. **Clone the repository or extract from a zip file:**

   - **Clone the repository:**

     Start by cloning the project repository from GitHub or your version control system.

     ```bash
     git clone https://github.com/your-repository.git
     cd your-repository
     ```

   - **Extract from a zip file:**

     If you have a zip file of the project, extract it to a directory of your choice.

     ```bash
     unzip your-repository.zip
     cd your-repository
     ```

2. **Set up a virtual environment:**

   ```bash
   python -m venv venv
3. **Activate the virtual environment::**

- On Mac/Linux:
   ```bash
   source venv/bin/activate
- On Windows:
   ```bash
   venv\Scripts\activate
4. **Install the project dependencies:**

   ```bash
   pip install -r requirements.txt
5. **Run migrations:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
2. **Run the development server:**

   ```bash
   python manage.py runserver
2. **Access the application:**

    Open your browser and navigate to:
   ```bash
   http://127.0.0.1:8000/



## Environment Variables

This project requires several API keys and sensitive credentials to function correctly. These should be stored in a `.env` file in the root directory of the project. Below is an example of what your `.env` file should look like:

```plaintext
# .env

# SSH Configuration
SSH_PASS = 'your_ssh_password'

# GitHub Token
TOKEN_GITHUB = 'your_github_token'

# API Keys

# Google API Key for Google services (e.g., Maps, YouTube, etc.)
GOOGLE_API_KEY = 'your_google_api_key'

# Search Engine ID for custom Google search integration.
SEARCH_ENGINE_ID = 'your_search_engine_id'

# FireCrawl API Key for web crawling services.
FIRECRAWL_API_KEY = 'your_firecrawl_api_key'

# OpenAI API Key for using OpenAI GPT models.
OPENAI_API_KEY = 'your_openai_api_key'

# BuiltWith API Key for accessing technology profile data.
BUILTWITH_API_KEY = 'your_builtwith_api_key'

# GROQ API Key for GROQ-based querying.
GROQ_API_KEY = 'your_groq_api_key'

# SendGrid
SENDGRID_API_KEY = 'your_sendgrid_api_key'


## Reference
- For more information about SSH configuration, refer to the [SSH Documentation](https://www.ssh.com/academy/ssh/config).
- To learn how to create a GitHub token and use it for authentication, refer to the [GitHub Token Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).
- For details on how to use the Google API, refer to the [Google API Documentation](https://developers.google.com/apis-explorer).
- Learn more about how to configure and use Custom Search Engine IDs at the [Google Custom Search Documentation](https://developers.google.com/custom-search/v1/introduction).
- For information about using FireCrawl, check out the [FireCrawl API Documentation](https://firecrawl.com/docs).
- For information about OpenAI's GPT API, refer to the [OpenAI API Documentation](https://beta.openai.com/docs/).
- To learn how to use the BuiltWith API, refer to the [BuiltWith API Documentation](https://api.builtwith.com/).
- For more information on the GROQ API, refer to the [GROQ API Documentation](https://www.sanity.io/docs/groq).
- For configuring and using SendGrid to send emails, refer to the [SendGrid API Documentation](https://docs.sendgrid.com/for-developers/sending-email/api-getting-started).
