# social-network API

A Django REST Framework–based social platform API with full user authentication (JWT), permissions and role-based access.
Features include posting, commenting, liking, following/followers system, feed generation based on followed users, bookmark system
and secure ownership validation for content CRUD.

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