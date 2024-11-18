from rest_framework.test import APITestCase
from .serializers import CatFactSerializer
from faker import Faker
from django.core.exceptions import ImproperlyConfigured
from unittest.mock import patch, MagicMock
from .factories import CatFactFactory
from django.test import override_settings
from .models import CatFact
from .views import FetchCatFactView
from django.conf import settings
import requests

class SerializerTest(APITestCase):
    def setUp(self):
        self.fake = Faker()

    def test_serializer_valid_data(self):
        data = {
            'fact': self.fake.sentence(nb_words=15),
            'length': self.fake.random_int()
        }
        serializer = CatFactSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, data)
        
    def test_serializer_empty_fact_and_length(self):
        data = {
            'fact': '',
            'length': ''  
        }
        serializer = CatFactSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('fact', serializer.errors)
        self.assertIn('length', serializer.errors)
    
    def test_serializer_empty_data_fact_validlength(self):
        invalid_data = {
            'fact': '',
            'length': self.fake.random_int()
        }
    
        serializer = CatFactSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('fact', serializer.errors) 
        
    def test_serializer_non_positive_length(self):
        invalid_data = {
            'fact': self.fake.sentence(nb_words=15),
            'length':-55
        }
        serializer = CatFactSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('length', serializer.errors) 

class FetchCatFactViewTest(APITestCase):
    
    def setUp(self):
        self.addCleanup(patch.stopall)  # Ensure patches are stopped after each test
    
    def test_add_facts_url_flag_successful_response(self):
        with override_settings(FETCH_URL="https://api.example.com/catfacts", FETCH_FLAG=True):
            self.assertIsInstance(settings.FETCH_URL, str)
            self.assertIsInstance(settings.FETCH_FLAG, bool)  
            with patch('requests.get') as mock_get:
                # Mock successful API response
                mock_data = CatFactFactory()
                mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_data)
                result = FetchCatFactView.add_facts()
                # Validate facts saved to the database
                saved_facts = CatFact.objects.all()
                self.assertEqual(len(saved_facts), 10) 
                self.assertEqual(len(result), 10)   
                for fact in saved_facts:
                    self.assertEqual(fact.fact, mock_data['fact'])
                    self.assertEqual(fact.length, mock_data['length'])

    def test_add_facts_disabled_fetch(self):
        with override_settings(FETCH_URL="ht5656we",FETCH_FLAG=False):
            self.assertIsInstance(settings.FETCH_URL, str)
            with patch('requests.get') as mock_get:
                # Test with FETCH_FLAG set to False
                result = FetchCatFactView.add_facts()
                mock_get.assert_not_called()
                self.assertEqual(CatFact.objects.count(), 0)
                self.assertEqual(result, [])
    
    def test_none_fetch_url(self):
        with override_settings(FETCH_URL=None,FETCH_FLAG=True):
            with self.assertRaises(ImproperlyConfigured) as cm:
                FetchCatFactView.add_facts()
                self.assertEqual(str(cm.exception), "FETCH_URL must not be None")

    def test_invalid_fetch_flag(self):
        with override_settings(FETCH_URL="http/uqerje/wdjfh..",FETCH_FLAG="false"):         
            with self.assertRaises(ImproperlyConfigured) as cm:
                FetchCatFactView.add_facts()
                self.assertEqual(str(cm.exception), "FETCH_FLAG must be a boolean")
    
    def test_none_fetch_flag(self):
        with override_settings(FETCH_URL="http/uqerje/wdjfh..",FETCH_FLAG=None):
            with self.assertRaises(ImproperlyConfigured) as cm:
                FetchCatFactView.add_facts()
                self.assertEqual(str(cm.exception), "FETCH_FLAG must not be None")            
    
    def test_invalid_fetch_url(self):
        with override_settings(FETCH_URL=345,FETCH_FLAG=True):          
            with self.assertRaises(ImproperlyConfigured) as cm:
                FetchCatFactView.add_facts()
                self.assertEqual(str(cm.exception), "FETCH_URL must be a string")

    def test_http_error_handling(self):
        with override_settings(FETCH_URL="https://api.com/catfacts", FETCH_FLAG=True):
            with patch('requests.get') as mock_get:
                # Mock a 404 Not Found response
                mock_response = MagicMock()
                mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
                mock_response.status_code = 404
                mock_get.return_value = mock_response
                result = FetchCatFactView.add_facts()
                self.assertEqual(result, [])
                mock_get.assert_called()
    
    def test_network_error_handling(self):
        with override_settings(FETCH_URL="https://api.com/catfacts", FETCH_FLAG=True):
            with patch('requests.get') as mock_get:
                # Mock a network error
                mock_get.side_effect = requests.exceptions.RequestException("Network Error")
                result = FetchCatFactView.add_facts()
                self.assertEqual(result, [])
                mock_get.assert_called()
                
    def test_unexpected_error_handling(self):
        with override_settings(FETCH_URL="https://api.com/catfacts", FETCH_FLAG=True):
            with patch('requests.get') as mock_get:
                # Mock an unexpected exception
                mock_get.side_effect = Exception("Unexpected Error")
                result = FetchCatFactView.add_facts()
                self.assertEqual(result, [])  # No facts should be saved on error
                mock_get.assert_called()

