# invoices/models.py
from django.db import models

class Invoice(models.Model):
    # Uploaded invoice image
    image = models.ImageField(upload_to='invoices/')
    
    # Generated Excel file
    excel_file = models.FileField(upload_to='excel/', blank=True, null=True)
    
    # Extracted data fields
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    vendor_name = models.CharField(max_length=255, blank=True, null=True)
    vendor_address = models.TextField(blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    
    # Optional: store full extracted text for reference/search
    extracted_text = models.TextField(blank=True, null=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Invoice {self.invoice_number or self.id}"

    class Meta:
        db_table = 'invoices'   # This sets the table name to `invoices`
