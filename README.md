# Corporatica Assessment Backend

This is a data processing application that reads multiple files and processes the data in order to generate charts and reports.

## Installation

1. Clone the repository
2. Run `pip install -r requirements.txt` to install the dependencies if you use python venv | Run `pipenv install` if you use pipenv
3. create a `.env` file in the root directory and add the following environment variables:
    ```
    SECRET_KEY=your_secret_key
    SQLALCHEMY_DATABASE_URI=e.g. postgresql://username:password@localhost/db_name
    MEDIA_FOLDER=e.g. "media"
    PROD_IMAGE=e.g. "prod_image"
    ```
4. Run `flask db upgrade` to create the database tables
5. Run `python masks.py` to populate the database with the mask data
6. Run `python random_csv.py` to generate random csv files in the `root` directory
7. Run `python run.py 0.0.0.0 8000 debug` to start the application

## Project Structure

```
    .
    ├── app
    │   ├── __init__.py
    │   ├── base_abstracts.py
    │   ├── db.py
    │   ├── helpers.py
    │   ├── medis_server.py
    │   ├── image_data
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── resources.py
    │   │   ├── schemas.py
    │   │   ├── service.py
    │   ├── tabular_data
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── resources.py
    │   │   ├── schemas.py
    │   │   ├── service.py
    │   ├── text_data
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── resources.py
    │   │   ├── schemas.py
    │   │   ├── service.py
    ├── migrations
    ├── nginx
    ├── .flake8
    ├── .pre-commit-config.yaml
    ├── docker-compose.yml
    ├── Dockerfile
    ├── masks.py
    ├── random_csv.py
    ├── README.md
    ├── requirements.txt
    ├── run.py
    |── entrypoint.sh
    |── gunicorn_config.py
    |── Pipfile
    |── Pipfile.lock
    |── pyproject.toml
```

## Packages Used

- Flask
- Flask-RESTful
- Flask-Migrate
- Flask-SQLAlchemy
- Flask-Cors
- Flask-marshmallow
- Marshmallow
- SQLAlchemy
- psycopg2
- gunicorn
- python-dotenv
- pandas
- matplotlib
- numpy
- pillow
- werkzeug
- nltk
- scikit-learn
- transformers
- pytorch


## Development Packages
- pre-commit
- flake8
- black
- isort
- autoflake

## Docker

To run the application in a docker container, follow the steps below:

1. Run `docker build -t $PROD_IMAGE .` to build the docker image
2. Run `docker compose up` to start the application

## API Endpoints

### Image Data /images
  - `/image` GET - Get all image data, POST - Add image data
  - `/image/multiple` POST - Add multiple image data
  - `/image/<int:id>` GET - Get image data by id, PUT - Update image data by id, DELETE - Delete image data by id
  - `/image/<int:id>/download` GET - Download image by id
  - `/image/<int:id>/convert` POST - Convert image to a specific format
  - `/image/<int:id>/resize` POST - Resize image
  - `/image/<int:id>/crop` POST - Crop image
  - `/image/<int:id>/mask/apply` POST - Apply mask to image
  - `/image/<int:id>/thumbnail/download` GET - Download image thumbnail by id
  - `/image/masks` GET - Get all masks data
  - `/image/<int:id>/rgb` POST - Change image RGB values

### Tabular Data /tabular
  - `/files/new` POST - Upload new csv file
  - `/files/<int:id>` GET - Get file data by id, PUT - Update file data by id, DELETE - Delete file data by id
  - `/files` GET - Get all file data

### Text Data /text
  - `/analysis` POST - Analyze text data
  - `/categorize` POST - Categorize text data against a specific categories
  - `/similarity` POST - Calculate similarity between base text and other list of texts
  - `/visualize` POST - Visualize text data against a list of texts using T-SNE algorithm
  - `/search` POST - Search text data against a specific query
  - `/wordcloud` POST - Generate wordcloud from text data

## Scripts

- `masks.py` - Populate the database with default masks data create if not exists
- `random_csv.py` - Generate random csv file to be used for tabular data testing
- `run.py` - Start the application

## Workflows

- `pre-commit` - Runs `black`, `isort`, `autoflake` and `flake8` on all files before commiting
- `docker-compose` - Runs the application in a docker container
- `.github/workflows/pr_lint.yml` - Runs `black`, `flake8`, `isort` on all files in the project when a PR is created on a specific branch
- `.github/workflows/deploy.yml` - Deploys the application to a specific server when a PR is merged to the production branch

## Author
- [Ahmed Saied](https://ahmedsaied.info/)
- [Linkedin](https://www.linkedin.com/in/ahmedsaied94/)
- [email](ahmed.saeed311294@gmail.com)
- [phone](https://wa.link/u55712)
- [github](https://github.com/AhmedSaied94)



