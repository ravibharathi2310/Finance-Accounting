from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Account, JournalEntry, Invoice, Bill, Payment
from .serializers import AccountSerializer, JournalEntrySerializer, InvoiceSerializer, BillSerializer, PaymentSerializer
from .models import SupplierBill, BankTransaction, ExpenseClaim, TaxRecord
from .serializers import SupplierBillSerializer, BankTransactionSerializer, ExpenseClaimSerializer, TaxRecordSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from .models import JournalLine, Invoice
from django.utils.dateparse import parse_date
from django.db import transaction
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class JournalEntryViewSet(viewsets.ModelViewSet):
    queryset = JournalEntry.objects.prefetch_related('lines').all()
    serializer_class = JournalEntrySerializer

    @action(detail=True, methods=['post'])
    def post_entry(self, request, pk=None):
        journal_entry = self.get_object()
        if journal_entry.posted:
            return Response({'status': 'already posted'}, status=status.HTTP_200_OK)
        total_debit = sum(line.debit for line in journal_entry.lines.all())
        total_credit = sum(line.credit for line in journal_entry.lines.all())
        if total_debit != total_credit:
            return Response({'error': 'Debit and credit not balanced'}, status=status.HTTP_400_BAD_REQUEST)
        from django.utils.timezone import now
        journal_entry.posted = True
        journal_entry.posted_at = now()
        journal_entry.save()
        return Response({'status': 'success', 'posted': True})

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """Return the current account balance (debits - credits)."""
        try:
            account = self.get_object()

            # Calculate sum of debits and credits from JournalLine for this account
            debit_sum = JournalLine.objects.filter(account_id=account.id).aggregate(Sum('debit'))['debit__sum'] or 0
            credit_sum = JournalLine.objects.filter(account_id=account.id).aggregate(Sum('credit'))['credit__sum'] or 0

            balance = debit_sum - credit_sum

            return Response({
                'account_id': str(account.id),
                'account_name': account.name,
                'balance': balance
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        invoice = self.get_object()
        if invoice.status == 'canceled':
            return Response({'detail': 'Invoice is already canceled.'}, status=status.HTTP_400_BAD_REQUEST)

        invoice.status = 'canceled'
        invoice.save()
        return Response({'detail': f'Invoice {invoice.invoice_no} canceled successfully.'})

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        invoice = self.get_object()
        if invoice.status == 'approved':
            return Response({'detail': 'Invoice is already approved.'}, status=status.HTTP_400_BAD_REQUEST)
        if invoice.status != 'issued':
            return Response({'detail': 'Only issued invoices can be approved.'}, status=status.HTTP_400_BAD_REQUEST)

        invoice.status = 'approved'
        invoice.save()
        return Response({'detail': f'Invoice {invoice.invoice_no} approved successfully.'})


class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        bill = self.get_object()
        if bill.status == 'approved':
            return Response({'detail': 'Bill already approved.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Your approval logic here:
        bill.status = 'approved'
        bill.save()
        
        return Response({'detail': f'Bill {bill.bill_no} approved successfully.'})

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @action(detail=True, methods=['post'], url_path='reconcile-with-bank')
    def reconcile_with_bank(self, request, pk=None):
        payment = self.get_object()

        # Your reconciliation logic here
        # Example: mark payment reconciled with a bank transaction
        bank_txn_id = request.data.get('bank_txn_id')
        if not bank_txn_id:
            return Response({'error': 'bank_txn_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Example update
        payment.bank_txn_id = bank_txn_id
        payment.status = 'reconciled'
        payment.save()

        return Response({'detail': f'Payment {payment.payment_no} reconciled with bank transaction {bank_txn_id}.'})

class SupplierBillViewSet(viewsets.ModelViewSet):
    queryset = SupplierBill.objects.all()
    serializer_class = SupplierBillSerializer

class BankTransactionViewSet(viewsets.ModelViewSet):
    queryset = BankTransaction.objects.all()
    serializer_class = BankTransactionSerializer

class BankTransactionViewSet(viewsets.ModelViewSet):
    queryset = BankTransaction.objects.all()
    serializer_class = BankTransactionSerializer

    @action(detail=False, methods=['get'], url_path='unmatched')
    def unmatched(self, request):
        unmatched_txns = self.queryset.filter(matched_payment_id__isnull=True)
        serializer = self.get_serializer(unmatched_txns, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='match')
    def match(self, request, pk=None):
        bank_txn = self.get_object()
        payment_id = request.data.get('payment_id')
        if not payment_id:
            return Response({'error': 'payment_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        bank_txn.matched_payment_id = payment_id
        bank_txn.save()
        return Response({'detail': f'Bank transaction {bank_txn.id} matched with payment {payment_id}.'})

class ExpenseClaimViewSet(viewsets.ModelViewSet):
    queryset = ExpenseClaim.objects.all()
    serializer_class = ExpenseClaimSerializer

class ExpenseClaimViewSet(viewsets.ModelViewSet):
    queryset = ExpenseClaim.objects.all()
    serializer_class = ExpenseClaimSerializer

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        claim = self.get_object()
        
        if claim.status == 'approved':
            return Response({'detail': 'Expense claim already approved.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update status and save
        claim.status = 'approved'
        claim.approved_by = request.user.id if request.user.is_authenticated else None
        claim.save()
        
        return Response({'detail': f'Expense claim {claim.id} approved.'})

class TaxRecordViewSet(viewsets.ModelViewSet):
    queryset = TaxRecord.objects.all()
    serializer_class = TaxRecordSerializer

class TrialBalanceView(APIView):
    def get(self, request):
        # Example simplified trial balance calculation
        date_str = request.query_params.get('date')
        as_of_date = parse_date(date_str) if date_str else None

        # Filter journal lines posted up to date
        journal_lines = JournalLine.objects.filter(
            journal_entry__posted=True,
        )
        if as_of_date:
            journal_lines = journal_lines.filter(journal_entry__date__lte=as_of_date)

        # Aggregate debit and credit sums by account
        balances = journal_lines.values('account_id').annotate(
            debit_sum=Sum('debit'),
            credit_sum=Sum('credit')
        )

        # Calculate net balance (debit - credit)
        result = []
        for bal in balances:
            net = (bal['debit_sum'] or 0) - (bal['credit_sum'] or 0)
            result.append({
                'account_id': bal['account_id'],
                'net_balance': net,
            })

        return Response(result)


class ProfitAndLossView(APIView):
    def get(self, request):
        from_date = parse_date(request.query_params.get('from', ''))
        to_date = parse_date(request.query_params.get('to', ''))

        # Filter P&L journal lines by COA types (simplified)
        journal_lines = JournalLine.objects.filter(
            journal_entry__posted=True,
            journal_entry__date__range=(from_date, to_date)
        ).filter(
            account_id__in=Account.objects.filter(type__in=['income', 'expense']).values_list('id', flat=True)
        )

        income = 0
        expense = 0
        for line in journal_lines:
            # Income accounts credit balance is profit
            acc_type = Account.objects.get(id=line.account_id).type
            net = (line.credit or 0) - (line.debit or 0) if acc_type == 'income' else (line.debit or 0) - (line.credit or 0)
            if acc_type == 'income':
                income += net
            else:
                expense += net

        pnl = income - expense
        return Response({'income': income, 'expense': expense, 'profit_or_loss': pnl})


class AgedReceivablesView(APIView):
    def get(self, request):
        as_of_date = parse_date(request.query_params.get('as_of'))
        if not as_of_date:
            return Response({'error': 'as_of query parameter required'}, status=400)

        invoices = Invoice.objects.filter(
            status__in=['issued', 'partial'],
            due_date__lte=as_of_date
        )

        # Categorize by aging buckets
        aging_buckets = {'0-30': 0, '31-60': 0, '61-90': 0, '90+': 0}

        for inv in invoices:
            delta_days = (as_of_date - inv.due_date).days
            amount = inv.balance_due or 0
            if delta_days <= 30:
                aging_buckets['0-30'] += amount
            elif delta_days <= 60:
                aging_buckets['31-60'] += amount
            elif delta_days <= 90:
                aging_buckets['61-90'] += amount
            else:
                aging_buckets['90+'] += amount

        return Response(aging_buckets)
    
class PartySummaryView(APIView):
    def get(self, request):
        party_id = request.query_params.get('party_id')
        if not party_id:
            return Response({'error': 'party_id query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        accounts = Account.objects.filter(id=party_id)
        summary = []
        for account in accounts:
            debit_sum = JournalLine.objects.filter(account_id=account.id).aggregate(total_debit=Sum('debit'))['total_debit'] or 0
            credit_sum = JournalLine.objects.filter(account_id=account.id).aggregate(total_credit=Sum('credit'))['total_credit'] or 0
            balance = debit_sum - credit_sum
            summary.append({
                'account_id': account.id,
                'account_name': account.name,
                'balance': balance
            })
        
        return Response({'party_id': party_id, 'accounts_summary': summary})



class InternalFundsTransferView(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data
        required_fields = ['from_account_id', 'to_account_id', 'amount', 'transfer_date']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return Response({'error': f'Missing fields: {", ".join(missing)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        from_account_id = data['from_account_id']
        to_account_id = data['to_account_id']
        amount = float(data['amount'])
        description = data.get('description', '')

        if amount <= 0:
            return Response({'error': 'Amount must be positive.'}, status=status.HTTP_400_BAD_REQUEST)
        if from_account_id == to_account_id:
            return Response({'error': 'From and To account must be different.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Example logic:
        from_account = Account.objects.filter(id=from_account_id).first()
        to_account = Account.objects.filter(id=to_account_id).first()
        if not from_account or not to_account:
            return Response({'error': 'Invalid from_account_id or to_account_id.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a journal entry for the transfer
        journal_entry = JournalEntry.objects.create(
            entry_no=f'TF-{from_account_id}-{to_account_id}-{data["transfer_date"]}',
            date=data['transfer_date'],
            narration=description,
            posted=True
        )

        # Debit from from_account
        JournalLine.objects.create(
            journal_entry=journal_entry,
            account_id=from_account_id,
            debit=0,
            credit=amount
        )
        # Credit to to_account
        JournalLine.objects.create(
            journal_entry=journal_entry,
            account_id=to_account_id,
            debit=amount,
            credit=0
        )

        return Response({'status': 'success', 'transfer_id': journal_entry.id})
    
class TrialBalancePDFView(APIView):
    def get(self, request):
        date_str = request.query_params.get('date')
        as_of_date = parse_date(date_str) if date_str else None

        journal_lines = JournalLine.objects.filter(journal_entry__posted=True)
        if as_of_date:
            journal_lines = journal_lines.filter(journal_entry__date__lte=as_of_date)

        balances = journal_lines.values('account_id').annotate(
            debit_sum=Sum('debit'),
            credit_sum=Sum('credit')
        )

        # Create the HttpResponse object with PDF headers.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="trial_balance.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter
        y = height - 50
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, y, "Trial Balance Report")
        y -= 40

        p.setFont("Helvetica", 12)
        p.drawString(50, y, "Account ID")
        p.drawString(150, y, "Debit")
        p.drawString(250, y, "Credit")
        p.drawString(350, y, "Balance")
        y -= 20

        for bal in balances:
            debit = bal['debit_sum'] or 0
            credit = bal['credit_sum'] or 0
            balance = debit - credit
            p.drawString(50, y, str(bal['account_id']))
            p.drawString(150, y, f"{debit:.2f}")
            p.drawString(250, y, f"{credit:.2f}")
            p.drawString(350, y, f"{balance:.2f}")
            y -= 20
            if y < 50:
                p.showPage()
                y = height - 50

        p.showPage()
        p.save()
        return response