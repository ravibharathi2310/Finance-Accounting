from django.test import TestCase
from rest_framework.test import APIClient

class FinanceTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_account_creation(self):
        response = self.client.post('/api/v1/finance/accounts/', {
            'code': '1000', 'name': 'Cash', 'type': 'asset'
        }, format='json')
        self.assertEqual(response.status_code, 201)
