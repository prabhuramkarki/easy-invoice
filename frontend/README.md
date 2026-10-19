# Easy Invoice frontend

React 19 and TypeScript interface for uploading invoice images to the Django OCR API and displaying the returned data. Styling uses Tailwind CSS 4; the development server uses Vite 7.

See the [root README](../README.md) for backend dependencies, MySQL/Tesseract setup, local CORS configuration, API examples, and current limitations.

## Run locally

Use Node.js 20.19+ within 20.x, or 22.12+, and npm. After starting the configured Django backend on `127.0.0.1:8000`, run from this directory:

```bash
npm install
npm run dev -- --port 5173 --strictPort
```

Use `npm install` for the initial setup: the checked-in npm lockfile omits the manifest's `lucide-react` dependency.

Open [http://localhost:5173](http://localhost:5173). Upload a JPG or PNG and choose **Extract Data**.

The upload URL is hardcoded to `http://127.0.0.1:8000/api/invoices` in [InvoiceForm.tsx](src/components/InvoiceForm.tsx). There is no API environment variable or Vite proxy configured. The backend must allow the frontend origin through CORS as described in the root README.

## Scripts

| Command | Purpose |
| --- | --- |
| `npm run dev` | Start Vite |
| `npm run build` | Run `tsc -b` and create the Vite build |
| `npm run lint` | Run ESLint |
| `npm run preview` | Preview a production build |

The strict TypeScript configuration exposes existing untyped handlers/state; a passing production build is not assumed. No frontend test script is configured.

Uploaded images, extracted text, and CSV summaries are retained by the backend despite the current footer wording. PDF input and Excel export are not implemented.
