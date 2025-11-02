from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccountViewSet,
    JournalEntryViewSet,
    InvoiceViewSet,
    BillViewSet,
    PaymentViewSet,
    TrialBalanceView,
    ProfitAndLossView,
    AgedReceivablesView,
)
from .views import SupplierBillViewSet, BankTransactionViewSet, ExpenseClaimViewSet, TaxRecordViewSet, PartySummaryView, InternalFundsTransferView, TrialBalancePDFView

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'journal-entries', JournalEntryViewSet, basename='journalentry')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'bills', BillViewSet, basename='bill')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'supplier-bills', SupplierBillViewSet, basename='supplierbill')
router.register(r'bank-transactions', BankTransactionViewSet, basename='banktransaction')
router.register(r'expense-claims', ExpenseClaimViewSet, basename='expenseclaim')
router.register(r'tax-records', TaxRecordViewSet, basename='taxrecord')


urlpatterns = [
    path('', include(router.urls)),
    path('reports/trial-balance/', TrialBalanceView.as_view(), name='trial-balance'),
    path('reports/pnl/', ProfitAndLossView.as_view(), name='profit-and-loss'),
    path('reports/aged-receivables/', AgedReceivablesView.as_view(), name='aged-receivables'),
    path('party-summary/', PartySummaryView.as_view(), name='party-summary'),
    path('internal-funds-transfer/', InternalFundsTransferView.as_view(), name='internal-funds-transfer'),
    path('trialbalance/pdf/', TrialBalancePDFView.as_view(), name='trialbalance-pdf'),
]
