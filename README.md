# Scotland Bird Predictor
This app is designed to predict bird species occurrence across Scotland. It uses a calibrated Random Forest classifier trained on 4.6M+ rows of eBird observation data. 
See bird species near a specific location, or see where a specific species is likely to occur across Scotland. 

**Live demo:** https://oliverlovatt.eu.pythonanywhere.com/

<!--- ![App screenshot](docs/images/app_screenshot.png) --->

## How it works
eBird data → filtering → features → Random Forest → calibrated predictions → offline-cached PWA

## Tech stack
Python | scikit-learn | Django | REACT

## Running it locally
```
  To run locally
  --------------
  Prerequisites: Python 3.11, Node.js + npm, PostgreSQL
  
  1. Extract the zip. All paths below are relative to the extracted
     project root (the folder containing pyproject.toml).
  
  Backend
  -------
  cd 3150919l_oliverlovatt_project
  
  Create and activate a Python 3.11 virtual environment:
      python -m venv venv
      venv\Scripts\activate
  
  pip install -r birdapp_backend/requirements.txt
  pip install -e .
  
  Ensure PostgreSQL is running, then create a database:
      - name:  birdapp_db
      - user:  postgres
      - host:  localhost, port 5432
  
  In birdapp_backend/, copy .env.example to .env and fill in:
      DB_PASSWORD
  
  cd birdapp_backend
  python manage.py migrate
  python manage.py load_predictions ..\predictions.csv
  python manage.py runserver
  
  Frontend (in a second terminal)
  -------------------------------
  cd 3150919l_oliverlovatt_project\birdapp-frontend
  npm install
  npm run dev
```
## Data
All prediction data comes from eBird, cross-validated with Bird Atlas.

## Author
Oliver Lovatt | MSc Software Development (Distinction) | University of Glasgow | [LinkedIn](www.linkedin.com/in/ollie-lovatt-073762193)
