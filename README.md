# AI Moderation Blog API

The goal of this project is to develop a streamlined API for managing posts and comments 
with integrated AI moderation and automated response functionality. 
Built using the Django Ninja framework, the system leverages GeminiAI 
for intelligent content moderation and Celery for automated response task handling, 
ensuring efficient processing of moderation tasks and automated replies.

## Authentication

To use the API, you need to create a user account and obtain a JWT token:

- **Register**: `POST /api/user/register`
- **Obtain token**: `POST /api/user/token/pair`
- **Verify token**: `POST /api/user/token/verify`
- **Refresh token**: `POST /api/user/token/refresh`

## Core Features

1. **User registration and JWT authentication**
   - Self-registration with username and password.
   - Login using JWT for secure access.

2. **Post management API**
   - Create, retrieve, update, and delete posts.
   - Each post is subject to AI-driven moderation to detect offensive language or inappropriate content before it is published.

3. **Comment management API**
   - Create, retrieve, update, and delete comments on posts.
   - Comments are also checked for offensive language, with options to block inappropriate comments.

4. **AI moderation**: 
   - Using GeminiAI automatically scans posts and comments for profanity, offensive language, or hate speech
   - Content failing the moderation check is flagged or blocked.

5. **Analytics on comments**
   - Provides a daily breakdown of comments over a specified period.
   - Example URL: `/api/comments/daily-breakdown?date_from=2024-10-23&date_to=2024-10-26`.
   - Returns aggregated statistics by day, showing the number of comments created and the number of blocked comments.

6. **Automated comment responses**
   - Users can enable automated responses to comments on their posts.
   - Responses are generated based on the content of the post and the comment, with a configurable delay set by the user.

7. **Access control**
   - Users can edit / delete only their own post and comments
   - Post author can delete comments related to his posts
   - Admins can delete all posts and comments


### Technical Stack

- **Framework**: [Django Ninja](https://django-ninja.dev/)
- **AI Moderation**: [GeminiAI](https://ai.google.dev/pricing) for free AI-based content moderation.
- **Background task processing**: [Celery](https://docs.celeryproject.org/) to handle delayed responses.

## Installation

> **Note:** The Gemini API and Google AI Studio may not be avaliablee in your region, and the AI Moderation feature will not work!
> **Consider using vpn. [List of available countries or territories](https://ai.google.dev/gemini-api/docs/available-regions)**

1. **Clone the repository**:
    ```
    git clone https://github.com/lilarin/AI-Moderation-Blog-API.git
    ```
2. **Create a virtual environment**:
    ```
    python -m venv env
    source env/bin/activate
    ```
### Run without docker:

1. **Install dependencies**:
    ```
    pip install -r requirements.txt
    ```
2. **Apply migrations**:
    ```
    python manage.py migrate
    ```
3. **Create a superuser**:
    ```
    python manage.py createsuperuser
    ```
4. **Run the development server**:
    ```
    python manage.py runserver
    ```
    > **Note**: Running the development server this way will not start 
    > Celery and auto-reply features will be unavailable.

5. (Optional) **Run the tests**:
    ```
    python manage.py test
    ```

### Run with Docker:

> **Note**: You can access to the docker terminal using command:
   ``docker-compose exec social_service sh``

1. **Launch Docker application**:

2. **Run the docker-compose**:
    ```
    docker-compose up --build
    ```
   
3. **Create a superuser**:
   ```
   python manage.py createsuperuser
   ```

4. (Optional) **Run the tests**:
    ```
    python manage.py test
    ```

## API Endpoints

- **Swagger documentation with all API endpoints**:
  - `/api/docs`
- **Admin panel**:
  - `/admin`

## Environment Variables

This project uses environment variables to manage sensitive 
settings like API keys, database configurations, etc. Ensure
you create a `.env` file based on `.env.sample` in the root directory and set
the required environment variables before running the project.

## Requirements
- **Python**: 3.8+ (recommended 3.12+)
- **PostgreSQL**: 13.0+
- **Redis**: 4.0+
