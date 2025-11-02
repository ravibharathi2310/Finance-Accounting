from rest_framework import serializers
from .models import Account, JournalEntry, JournalLine, Invoice, Bill, Payment
from rest_framework import serializers
from .models import SupplierBill, BankTransaction, ExpenseClaim, TaxRecord

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class JournalLineSerializer(serializers.ModelSerializer):
    journal_entry = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = JournalLine
        fields = '__all__'


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalLineSerializer(many=True)

    class Meta:
        model = JournalEntry
        fields = ['id', 'entry_no', 'date', 'narration', 'posted', 'posted_at', 'meta', 'created_at', 'lines']

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        entry = JournalEntry.objects.create(**validated_data)
        for line_data in lines_data:
            JournalLine.objects.create(journal_entry=entry, **line_data)
        return entry


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class SupplierBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierBill
        fields = '__all__'

class BankTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankTransaction
        fields = '__all__'

class ExpenseClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseClaim
        fields = '__all__'

class TaxRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRecord
        fields = '__all__'