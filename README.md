# Mini Reconciliation API

A Django REST API for financial reconciliation between internal records(eg. from ecommerce syatem) and provider records(eg. from payment gateway).

## Features

- File-based reconciliation system
- CSV file parsing and processing
- RESTful API endpoints
- Automated matching and discrepancy detection

## Project Structure

- `reconciliation_api/`: Main Django project directory
- `reconciliation_app/`: Django app containing the business logic
- `db.sqlite3`: SQLite database file
- `.github/`: GitHub Actions workflows

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install django djangorestframework
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### Available Endpoints

- `GET /api/` - List available API endpoints
- `POST /api/reconcile/` - Upload and reconcile files

### Reconciliation API

#### POST /api/reconcile/

Upload two CSV files for reconciliation:
- `internal_file`: Internal records CSV file
- `provider_file`: Provider records CSV file

Example request:
```bash
curl -X POST http://localhost:8000/api/reconcile/ \
  -F "internal_file=@internal_records.csv" \
  -F "provider_file=@provider_records.csv"
```

## CSV File Format

The API expects CSV files with the following fields:
- transaction_reference (string)
- amount (numeric)
- status (string)
- transaction_date (string)
- description (string)

## Development

The project uses GitHub Actions for continuous integration and deployment.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For support, please open an issue in the GitHub repository.
