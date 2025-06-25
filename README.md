VNDLV Project

Vehicle and Driver License Verification System

This web-based system allows users to verify vehicle registration plates and driver licenses. It provides an interface for users to report suspicious credentials and enables administrators to review submissions and generate reports in CSV and PDF formats.



Features

-  User login and role-based access control
-  Verify vehicle number plates
-  Verify driver license IDs
-  Submit and track issue reports
-  Admin panel with filters, feedback, and report download options
-  Export reports as CSV or PDF
-  Simple and responsive web interface



Technologies Used

- Backend: Python (Flask)
- Frontend: HTML, CSS, JavaScript (jQuery)
- Database: MySQL
- PDF Export: WeasyPrint
- Environment Management: python-dotenv

---

Project Structure


Vndlv_project/
├── app.py                # Main Flask app with route handlers
├── database.py           # Database connection and helper functions
├── .env                  # Environment variables (example format below)
├── requirements.txt      # Python package dependencies
│
├── templates/            # HTML templates for all pages
├── static/               # CSS and JS files
└── README.md             # Project documentation




 Setup Instructions

 1. Clone the Repository

bash
git clone https://github.com/Bambi-Sam99/vndlv-system.git
cd Vndlv_project


 2. Create a Virtual Environment (optional but recommended)

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


 3. Install Required Packages

bash
pip install -r requirements.txt


 4. Configure Environment Variables

Create a .env file in the root folder with the following format:

env
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=vndlv_db
SECRET_KEY=your_secret_key_here


5. Set Up the Database

- Use MySQL to create a database called `vndlv_db`
- Populate it with tables: `Users`, `Vehicles`, `Drivers`, `Reports`
- Optional: Include a starter SQL script (`init_db.sql`) if you have one

 6. Run the Application

bash
python app.py


Visit `http://127.0.0.1:5000` in your browser.


License

This project is provided for academic and educational purposes.


Acknowledgements

Developed by:
- SYLVESTER DASSAH  10303382
- MOHAMMED ABDUL HAFIZ 10303393
- CLINTON ARMOH BOADI 10303351

As part of Project Work 
Institution: University of Professional Studies, Accra (UPSA)


Contributing

This project is open for learning collaboration. Fork it, improve it, or suggest features!
