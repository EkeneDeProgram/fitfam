## Project Setup

### Prerequisites
- Python
- MySQL

### Installation
1. Create a virtual environment:
   ```sh
   python -m venv env
   ```

2. Activate the virtual environment:
   ```sh
   env\Scripts\activate
   ```

3. Install dependencies using pip:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up the environment variables:
   -  rename the .env.example file to .env
   -  Open the .env file and set the SECRET_KEY and DATABASE_URL variable to your MySQL connection URI.
   ```sh
   DATABASE_URL=mysql://your_username:your_password@localhost/your_database_name
   SECRET_KEY=your_secret_key
   ```

5. Initialize a new Flask-Migrate environment in your project:
   ```sh
   flask db init
   ```

6. Create a new migration script based on your SQLAlchemy models:
   ```sh
   flask db migrate -m "Create user table"
   ```

7. Apply the migration to the database:
   ```sh
   flask db upgrade
   ```

### Running the Application
1. Run the development server:
   ```sh
   python app.py
   ```

2. Open your browser and navigate to http://127.0.0.1:5000/ to access the web application.

