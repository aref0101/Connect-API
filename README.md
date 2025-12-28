# social-network API

Developed a Django REST Framework–based social platform API with JWT authentication, fine-grained permissions, and secure ownership validation. 
Implemented core social features including posts, comments, likes, block, follow/follower system, private accounts, feed generation based on followed users, bookmarks, and cursor pagination. 
Optimized database performance by eliminating N+1 queries using select_related and ORM annotations (Count, Exists), and reduced query cost on like/follow operations through composite indexing and query-aware Django ORM design.

---

## Features

- **User Auth**  
User registration and login are implemented using JSON Web Tokens (JWT) via Simple JWT, with full support for token refresh and rotation to ensure secure and seamless authentication. 

- **API Niceties**   
  - **Commenting**: you can write comment for posts.
  - **Liking**: you can like and unlike posts.
  - **Following**: you can follow and unfollow users.
  - **Bookmarking**: you can bookmark (save) anyone's posts.
  - **Blocking**: blocked users don't access to your posts and its comments. 
  - **Private account**: you are not allowed to view the posts and its comments of a private account or like and bookmark them, Unless you request to follow them and they accept it.

---

## Tech Stack

- **Python**  
- **Django**  
- **Django REST Framework**  
- **djangorestframework-simplejwt**  
- **PostgreSQL** 

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