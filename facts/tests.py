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

class SerializerTest(APITestCase):
    def setUp(self):
        self.fake = Faker()

    def test_serializer_valid_data(self):
        data = {
            'fact': self.fake.sentence(nb_words=15),
            'length': self.fake.random_int()
        }
        print(data)
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
        print(invalid_data)
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
    
    @override_settings(FETCH_URL="ht5656we", FETCH_FLAG=True)
    def test_add_facts_url_flag_successful_response(self):
        self.assertIsInstance(settings.FETCH_URL, str)
        self.assertIsInstance(settings.FETCH_FLAG, bool)  
        with patch('requests.get') as mock_get:
            # Mock successful API response
            mock_data = CatFactFactory()
            mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_data)
            
            with patch('logging.Logger.info') as mock_logger:
            # Call the view method to fetch and save data
                result = FetchCatFactView.add_facts()
            # Validate facts saved to the database
                saved_facts = CatFact.objects.all()
                self.assertEqual(len(saved_facts), 10) 
                self.assertEqual(len(result), 10)  
                mock_logger.assert_any_call("Fetching cat fact....")
                self.assertTrue(
                    any(call[0][0].startswith("Serializer data is valid:")for call in mock_logger.call_args_list)
                )   
                self.assertTrue(
                    any(call[0][0].startswith("CatFacts saved successfully:")for call in mock_logger.call_args_list)
                )     
                for fact in saved_facts:
                    self.assertEqual(fact.fact, mock_data['fact'])
                    self.assertEqual(fact.length, mock_data['length'])

    @override_settings(FETCH_URL="ht5656we",FETCH_FLAG=False)
    def test_add_facts_disabled_fetch(self):
        self.assertIsInstance(settings.FETCH_URL, str)
        with patch('requests.get') as mock_get:
            with patch('logging.Logger.info') as mock_logger:
                # Test with FETCH_FLAG set to False
                result = FetchCatFactView.add_facts()
                mock_logger.assert_any_call("Fetching cat fact....")
                self.assertTrue(
                    any(call[0][0].startswith("Fetch is disabled in settings")for call in mock_logger.call_args_list)
                )  
                mock_get.assert_not_called()
                self.assertEqual(CatFact.objects.count(), 0)
                self.assertEqual(result, [])
      
    @override_settings(FETCH_URL="http/uqerje/wdjfh..",FETCH_FLAG="false") 
    def test_invalid_fetch_flag(self):         
        with self.assertRaises(ImproperlyConfigured) as cm:
            FetchCatFactView.add_facts()
            self.assertEqual(str(cm.exception), "FETCH_FLAG must be a boolean")
            
    @override_settings(FETCH_URL=345,FETCH_FLAG=True) 
    def test_invalid_fetch_url(self):         
        with self.assertRaises(ImproperlyConfigured) as cm:
            FetchCatFactView.add_facts()
            self.assertEqual(str(cm.exception), "FETCH_URL must be a string")
    
    @override_settings(FETCH_URL="ht5656we", FETCH_FLAG=True)
    def test_failed_api_response_logs_error(self):
        self.assertIsInstance(settings.FETCH_URL, str)
        self.assertIsInstance(settings.FETCH_FLAG, bool)
        with patch('requests.get') as mock_get:
            # Mock failed API response
            mock_get.return_value = MagicMock(status_code=500)
            with patch('logging.Logger.error') as mock_error_logger:
                # Call the view method to simulate API failure
                result = FetchCatFactView.add_facts()
                mock_error_logger.assert_any_call("Failed to fetch data from API.Status code: 500")
                self.assertEqual(CatFact.objects.count(), 0)
                self.assertEqual(result, [])
    