## Welcome to the Online shop project! This is a Django-based web application designed to facilitate an online shopping experience, featuring user authentication, product listings, and discount management. The project utilizes Django REST Framework to create a robust API for communication between the front end and back end.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [database_set_up](#database-set-up)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## Features

- User authentication (registration, login, logout)
- Product management (CRUD operations for products)
- Discount management (CRUD operations for discounts)
- RESTful API for front-end integration
- Secure and scalable architecture
- Dockerized for easy deployment and environment consistency

## Technologies Used

- Python 3.x
- Django 3.x+
- Django REST Framework
- postgresql
- Git for version control

## database_set_up

   To set up the PostgreSQL database for this Django project, follow these steps:

   ### Requirements
   
      PostgreSQL installed on your machine or access to a PostgreSQL server.
      A database management tool (optional, e.g., pgAdmin, DBeaver) to manage your databases.
      
   ### Step 1: Create a PostgreSQL Database
   
      Open your terminal or command line interface.
      Access the PostgreSQL command line by running:

      
      ```bash
      psql -U postgres

      CREATE DATABASE your_database_name;
      
      CREATE USER your_username WITH PASSWORD 'your_password';

      GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_username;

      \q
   ### step 2:Update Database Settings in Django

      In your Django project, you need to configure the database settings in the settings.py file.

      Open settings.py located in your Django project directory.
      Locate the DATABASES setting and update it as follows:
      
      
       ```bash
       DATABASES = {
        'default': {
         'ENGINE': 'django.db.backends.postgresql',
         'NAME': 'your_database_name',  # Your database name
         'USER': 'your_username',        # Your database username
         'PASSWORD': 'your_password',    # Your database password
         'HOST': 'localhost',            # Set to 'localhost' for local development
         'PORT': '5432',                 # Default PostgreSQL port
           }
       }




## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/FATEMEfati/Online_Shop_backend.git
   cd online_shop_backend

2.  **Create a virtual environment:**
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate

3.  **Install the required packages:**
    ```bash
    pip install -r requarment

4.  **Set up the database:**
    ```bash
    python manage.py migrate
5.  **Create a superuser (optional):**
    ```bash
    python manage.py createsuperuser

6.  **Run the development server:**
    ```bash
    python manage.py runserver
7.  **Open your browser and navigate to:**
    ```bash
    http://127.0.0.1:8000/

## Docker Installation

If you prefer to run the project using Docker, you can do so by following these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/FATEMEfati/Online_Shop_backend.git
   cd online_shop_backend

2. **Build the Docker containers:**
   ```bash
   docker-compose build

3. **Run the Docker containers:**
   ```bash
   docker-compose up
4. **Set up the database: In a new terminal, run:**
    ```bash
    docker-compose exec web python manage.py migrate
    
5. **Create a superuser (optional): You can also create a superuser by running:**
    ```bash
    docker-compose exec web python manage.py createsuperuser


## Usage
After setting up the project, you can use the API to perform various operations related to users, products, and discounts. You can also access the Django admin panel at http://127.0.0.1:8000/admin/ using the superuser credentials you created.
## API Endpoints
**Below are some of the key API endpoints available in the application:**

**Users**
GET api-v1/users/

POST api-v1/login

POST api-v1/token/

POST pi-v1/token/refresh/

POST api-v1/register_users/

**Products**
GET api-v1/products/

GET api-v1/categories/

POST api-v1/search

GET api-v1/product_for_cat/{id}/

**Discounts**
GET api-v1/gift cart/

**Orders**
GET api-v1/orders/{order-id}

GET api-v1/orderItem/{order-id}

GET api-v1/top_product/

GET api-v1/top_categories/

POST api-v1/create_order/

GET api-v1/show_cart/

##   Project Structure
     online_shop_backend/
     ├── manage.py
     ├── requarment
     ├── online_shop/
     │   ├── settings.py
     │   ├── urls.py
     │   └── wsgi.py
     ├── users/
     │   ├── models.py
     │   ├── views.py
     │   └── ...
     ├── products/
     │   ├── models.py
     │   ├── views.py
     │   └── ...
     ├── Orders/
     │   ├── models.py
     │   ├── views.py
     │   └── ...
     └── discounts/
         ├── models.py
         ├── views.py
         └── ...

## Contributing
Contributions are welcome! If you want to contribute to the project, please follow these steps:

1.Fork the repository.
2.Create a new branch (git checkout -b feature/YourFeature).
3.Make your changes.
4.Commit your changes (git commit -m 'Add some feature').
5.Push to the branch (git push origin feature/YourFeature).
6.Open a pull request.

Thank you for checking out the Online Store project! If you have any questions or feedback, feel free to reach out.
