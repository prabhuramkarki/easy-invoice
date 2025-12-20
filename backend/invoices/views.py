from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Invoice
from .serializers import InvoiceSerializer

from PIL import Image
import pytesseract
import csv
import os
import re
from datetime import datetime
from django.conf import settings


class InvoiceViewSet(viewsets.ModelViewSet):

    queryset = Invoice.objects.all().order_by('-created_at')
    serializer_class = InvoiceSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        invoice = serializer.save()

        # Correct image field
        image_path = invoice.image.path

        # OCR text extraction
        text = pytesseract.image_to_string(
            Image.open(image_path).convert('L')
        )

        # Save full extracted text
        invoice.extracted_text = text

        # Extract fields using regex
        invoice_number = re.search(r'Invoice\s*Number[:\s]*([A-Za-z0-9-]+)', text)
        total_amount = re.search(r'Total[:\s]*([\d.,]+)', text)
        invoice_date = re.search(r'Date[:\s]*(\d{2}/\d{2}/\d{4})', text)
        vendor_name = re.search(r'From[:\s]*(.+)', text)

        # Assign values to model
        if invoice_number:
            invoice.invoice_number = invoice_number.group(1)

        if total_amount:
            invoice.total_amount = total_amount.group(1).replace(',', '')

        if invoice_date:
            invoice.invoice_date = datetime.strptime(
                invoice_date.group(1), '%d/%m/%Y'
            ).date()

        if vendor_name:
            invoice.vendor_name = vendor_name.group(1).strip()

        # Save updated invoice object
        invoice.save()

        # CSV file path
        csv_path = os.path.join(settings.MEDIA_ROOT, 'invoices.csv')

        # Create CSV header if file not exists
        if not os.path.exists(csv_path):
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Invoice Number',
                    'Invoice Date',
                    'Vendor Name',
                    'Total Amount',
                    'Image Path'
                ])

        # Append invoice data
        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                invoice.invoice_number,
                invoice.invoice_date,
                invoice.vendor_name,
                invoice.total_amount,
                image_path
            ])
