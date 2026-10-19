# Easy Invoice

Easy Invoice is an invoice image OCR project with a React upload interface and a Django REST API. Upload a JPG or PNG, extract text with Tesseract, view the returned invoice fields, and append the extracted summary to a server-side CSV file.

This is a development prototype. PDF processing and Excel export are not implemented, and local setup currently requires the dependency and CORS configuration described below.

## What it does

- Accepts an invoice image through file selection or drag and drop.
- Converts the image to grayscale and runs Tesseract OCR synchronously during upload.
- Extracts an invoice number, date, vendor, and total using regular expressions.
- Stores the image, full OCR text, and invoice record; appends a summary to `backend/media/invoices.csv`.
- Provides REST endpoints for listing, retrieving, updating, and deleting invoice records.

The parser looks for `Invoice Number`, `Date` in `dd/mm/yyyy` format, `From`, and `Total`. These matches depend on both the invoice layout and OCR accuracy; check the extracted values against the original image.

## Stack and layout

| Directory | Purpose |
| --- | --- |
| [frontend](frontend/) | React 19, TypeScript, Vite 7, Tailwind CSS 4, and Lucide icons |
| [backend](backend/) | Django project generated with Django 6.0, Django REST Framework, MySQL, Pillow, and pytesseract |
| [backend/invoices](backend/invoices/) | Invoice model, serializer, API viewset, and OCR/CSV processing |

## Requirements

- Python **3.12–3.14** for [Django 6.0](https://docs.djangoproject.com/en/6.0/faq/install/#what-python-version-can-i-use-with-django), plus pip and virtual environment support.
- MySQL compatible with Django 6.0, a local database, and credentials with permission to create application tables.
- The **Tesseract OCR executable** installed separately and available on `PATH`; installing `pytesseract` alone does not install the OCR engine.
- A compiler, Python development headers, and MySQL client development libraries if your platform needs to build `mysqlclient`.
- Node.js **20.19+ within 20.x, or 22.12+**, and npm for Vite 7.

## Local setup

### 1. Backend dependencies

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install 'Django>=6.0,<6.1' djangorestframework mysqlclient django-cors-headers
tesseract --version
```

On Windows, activate the environment with `.venv\Scripts\activate` instead. Install Tesseract using your platform's package manager or installer before running the last command.

The second pip command is necessary because the checked-in `requirements.txt` omits Django, Django REST Framework, and the MySQL driver. `django-cors-headers` is needed for the separate browser frontend in the setup below. No complete pinned Python dependency set is supplied.

### 2. Database configuration

Create an empty MySQL database named `easy_invoice`, or choose another name. Update `DATABASES['default']` in [backend/config/settings.py](backend/config/settings.py) with your local database name, username, password, host, and port. The committed values are development placeholders.

Settings currently read these values directly from Python; creating a `.env` file does not configure the database, even though `python-dotenv` appears in the requirements.

### 3. Allow the local frontend origin

The frontend posts directly to `http://127.0.0.1:8000/api/invoices`, while Vite serves the page on port 5173. CORS is not configured in the checked-in backend, so the browser flow needs this local settings change.

In `backend/config/settings.py`, add `"corsheaders"` to the existing `INSTALLED_APPS` list and add `"corsheaders.middleware.CorsMiddleware"` near the top of the existing `MIDDLEWARE` list, before `"django.middleware.common.CommonMiddleware"`. Keep all existing apps and middleware. Then add:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```

See the [django-cors-headers setup instructions](https://github.com/adamchainz/django-cors-headers#setup). Restart Django after changing settings. Use the actual frontend origin if you choose a different port.

### 4. Start Django

From `backend`, with the virtual environment active and MySQL running:

```bash
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

The API is available at [http://127.0.0.1:8000/api/invoices](http://127.0.0.1:8000/api/invoices). To use Django's admin interface, run `python manage.py createsuperuser` separately and visit `/admin/`.

### 5. Start React

In another terminal, from the repository root:

```bash
cd frontend
npm install
npm run dev -- --port 5173 --strictPort
```

Use `npm install` for the initial setup: the checked-in npm lockfile omits the manifest's `lucide-react` dependency.

Open [http://localhost:5173](http://localhost:5173). Select a readable image, choose **Extract Data**, and compare the returned fields with the source invoice. The API URL is hardcoded in [InvoiceForm.tsx](frontend/src/components/InvoiceForm.tsx); no frontend API environment variable is currently implemented.

## API examples

The router is configured **without trailing slashes**. With Django running, upload an image using the multipart field name `image`:

```bash
curl -X POST http://127.0.0.1:8000/api/invoices \
  -F 'image=@/absolute/path/to/invoice.png'

curl http://127.0.0.1:8000/api/invoices
curl http://127.0.0.1:8000/api/invoices/1
```

Replace the image path with a real JPG/PNG and the record ID with one returned by the API. A successful creation returns the serialized invoice, including `id`, `image`, `extracted_text`, and the extracted fields. Fields without matching text can be `null`.

| Method | Path | Purpose |
| --- | --- | --- |
| GET / POST | `/api/invoices` | List records / upload and process an image |
| GET | `/api/invoices/{id}` | Retrieve a record |
| PUT / PATCH | `/api/invoices/{id}` | Update fields using multipart/form data |
| DELETE | `/api/invoices/{id}` | Delete a database record |

OCR and CSV append run only when creating a record. Editing a record does not rerun OCR or update the existing CSV row. The shared CSV is written on the server; the UI has no download button.

## Development commands

| Directory | Command | Purpose |
| --- | --- | --- |
| `frontend` | `npm run dev` | Start Vite |
| `frontend` | `npm run build` | Type-check with TypeScript and build with Vite |
| `frontend` | `npm run lint` | Run ESLint |
| `frontend` | `npm run preview` | Preview a frontend build |
| `backend` | `python manage.py check` | Check Django project configuration |
| `backend` | `python manage.py test` | Run Django tests |

These are available commands, not verified passing checks. The frontend contains untyped handlers/state that need attention under its strict TypeScript settings. `backend/invoices/tests.py` is a placeholder, and no frontend test script is configured.

## Current limitations and data handling

- **Images only:** there is no PDF conversion or processing path. The `excel_file` model field and `openpyxl` dependency do not currently produce XLSX exports.
- **Data is retained:** uploaded images go to `backend/media/invoices/`; OCR text and fields go to MySQL; CSV summaries go to `backend/media/invoices.csv`. The frontend's “not stored” footer does not describe the implemented behavior.
- **Local use:** the API has no configured authentication or per-user permissions. Debug mode, a committed development secret, and local media serving are enabled. Complete deployment configuration and access controls before uploading sensitive invoices or exposing the service.
- **Processing is basic:** OCR runs inside the request, and unexpected OCR/date/amount errors can fail after an image or record has already been saved. CSV writes have no concurrency coordination.
- **Deletion is partial:** deleting a database record does not remove its existing CSV row or automatically clean up its uploaded image.
