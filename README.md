🛒 Django Ecommerce Website

A full-stack Ecommerce Web Application built using Django, featuring user authentication, product management, cart functionality, and admin controls.
This project is designed for learning, real-world practice, and portfolio use.

🚀 Features
👤 User Features

User Registration & Login

Forgot Password functionality

Product listing with images

Product detail page

Add to Cart

View Cart

Secure checkout flow

Responsive UI (HTML + CSS)

🛠 Admin Features

Admin Login

Admin Dashboard

Add / Update / Delete Products

View users and orders (extendable)

🧰 Tech Stack

Backend: Django (Python)

Frontend: HTML, CSS

Database: SQLite3 (default)

Authentication: Django Auth System

Media Handling: Django Media Files

Version Control: Git & GitHub

📂 Project Structure
Ecommerce/
│
├── eco/                 # Main Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── store/               # Ecommerce app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   └── static/
│
├── media/               # Product images
├── db.sqlite3           # Database
├── manage.py
└── README.md

⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/KavitaSinghPanwar/Ecommerce-Django.git
cd Ecommerce-Django

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # macOS/Linux

3️⃣ Install Dependencies
pip install django

4️⃣ Run Migrations
python manage.py makemigrations
python manage.py migrate

5️⃣ Create Superuser
python manage.py createsuperuser

6️⃣ Run the Server
python manage.py runserver


Open browser:

http://127.0.0.1:8000/


Admin panel:

http://127.0.0.1:8000/admin/

🔐 Authentication Flow

Users can Sign Up / Login

Admin manages products via Admin Dashboard

Session-based authentication using Django

🖼 Media & Static Files

Product images are stored in /media/products/

Static files handled via Django static settings

🧪 Future Enhancements

Payment Gateway Integration

Order History

Wishlist Feature

Product Search & Filters

Deployment (Render / Railway / AWS)

REST API using Django REST Framework

📌 Important Notes

Do NOT upload:

db.sqlite3

media/

__pycache__/

.env

Use .gitignore for production projects.

👩‍💻 Author

Kavita Singh Panwar
Aspiring Full-Stack Developer
Focused on Django, Flask & Backend Systems

⭐ Support

If you like this project:

⭐ Star the repository

🍴 Fork it

🛠 Improve & contribute
