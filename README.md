# SocialNetwork API

A Django REST Framework–based web API. Only the authenticated owner of a post or comment is authorized to modify or delete it. The system includes user login and registration, JWT-based authentication, and a full suite of features such as comment, like, bookmark, follow, a feed based on user followings and list of users following and followers (e.g., “Known issue: image field resets on update; planned fix in next version”),

---

## Features

- **User Auth**  
User registration and login are implemented using JSON Web Tokens (JWT) via Simple JWT, with full support for token refresh and rotation to ensure secure and seamless authentication. 

- **API Niceties**   
  - **Commenting**: you can write comment for posts.
  - **Liking**: you can like and unlike posts.
  - **Following**: you can follow and unfollow users.
  - **Bookmarking**: you can bookmark (save) anyone's posts.

---

## Tech Stack

- **Python 3.x**  
- **Django 4.x**  
- **Django REST Framework**  
- **djangorestframework-simplejwt**  
- **SQLite** 

---

## 📥 Installation

1. **Clone it**  
   ```bash
   git clone https://github.com/aref0101/Connect-API.git
   cd Connect-API

# 2. Create & activate a virtualenv
python -m venv .venv

source .venv/bin/activate      # macOS/Linux

.venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
SECRET_KEY= your-secret-key

DEBUG= True   # switch to False in production

ALLOWED_HOSTS= 127.0.0.1, localhost

# 5. python manage.py migrate
python manage.py migrate

# 6. Create a superuser
python manage.py createsuperuser

# 7. start the project
python manage.py runserver