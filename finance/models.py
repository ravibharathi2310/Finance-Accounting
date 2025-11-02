from django.db import models
from django.db.models import CASCADE

class Account(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=32)
    parent_account_id = models.IntegerField(null=True, blank=True)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    meta = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_accounts'


class JournalEntry(models.Model):
    id = models.AutoField(primary_key=True)
    entry_no = models.CharField(max_length=64, unique=True, null=True, blank=True)
    date = models.DateField()
    narration = models.TextField(null=True, blank=True)
    posted = models.BooleanField(default=False)
    posted_at = models.DateTimeField(null=True, blank=True)
    meta = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finance_journal_entries'


class JournalLine(models.Model):
    id = models.AutoField(primary_key=True)
    journal_entry = models.ForeignKey(JournalEntry, on_delete=CASCADE, related_name='lines')
    account_id = models.IntegerField(null=True, blank=True)
    debit = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    party_type = models.CharField(max_length=50, null=True, blank=True)
    party_id = models.IntegerField(null=True, blank=True)
    tax_details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finance_journal_lines'


class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    invoice_no = models.CharField(max_length=50, unique=True)
    customer_id = models.IntegerField(null=True, blank=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=32, default='draft')
    line_items = models.JSONField(default=list)
    sub_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_invoices'


class Bill(models.Model):
    id = models.AutoField(primary_key=True)
    bill_no = models.CharField(max_length=50, unique=True)
    supplier_id = models.IntegerField(null=True, blank=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=32, default='draft')
    line_items = models.JSONField(default=list)
    sub_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_bills'


class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    payment_no = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=8, default='INR')
    payment_date = models.DateField()
    method = models.CharField(max_length=50)
    from_account_id = models.IntegerField(null=True, blank=True)
    to_account_id = models.IntegerField(null=True, blank=True)
    related_invoices = models.JSONField(null=True, blank=True)
    related_bills = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=32, default='posted')
    reference = models.CharField(max_length=255, null=True, blank=True)
    bank_txn_id = models.IntegerField(null=True, blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_payments'


class SupplierBill(models.Model):
    id = models.AutoField(primary_key=True)
    bill_no = models.CharField(max_length=50, unique=True)
    supplier_id = models.IntegerField(null=True, blank=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=32, default='draft')
    line_items = models.JSONField(default=list)
    sub_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    balance_due = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_by = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finance_supplier_bills'


class BankTransaction(models.Model):
    id = models.AutoField(primary_key=True)
    bank_account_id = models.IntegerField(null=True, blank=True)
    txn_date = models.DateField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    txn_type = models.CharField(max_length=16)  # credit or debit
    description = models.TextField()
    reference = models.CharField(max_length=255)
    imported_from = models.JSONField(null=True, blank=True)
    matched_payment_id = models.IntegerField(null=True, blank=True)
    reconciled = models.BooleanField(default=False)
    reconciled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finance_bank_transactions'


class ExpenseClaim(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.IntegerField(null=True, blank=True)
    claim_date = models.DateField()
    items = models.JSONField()
    total = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=32)  # submitted, approved, paid, rejected
    approved_by = models.IntegerField(null=True, blank=True)
    payment_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finance_expense_claims'


class TaxRecord(models.Model):
    id = models.AutoField(primary_key=True)
    return_period = models.DateField()
    tax_type = models.CharField(max_length=32)
    taxable_amount = models.DecimalField(max_digits=18, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2)
    source = models.JSONField()
    file_meta = models.JSONField(null=True, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32)

    class Meta:
        db_table = 'finance_tax_records'
