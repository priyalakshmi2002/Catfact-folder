from rest_framework.test import APITestCase
from .serializers import CatFactSerializer
from faker import Faker
from django.core.exceptions import ImproperlyConfigured
from unittest.mock import patch, MagicMock
from .factories import CatFactFactory
from .models import CatFact
from .views import FetchCatFactView
from django.conf import settings
import requests

class SerializerTest(APITestCase):
    '''Verifies serilaizers'''
    def setUp(self):
        self.fake = Faker()

    def test_serializer_valid_data(self):
        '''Verifies successful validation of CatFactSerializer with valid input'''
        data = {
            'fact': self.fake.sentence(nb_words=15),
            'length': self.fake.random_int()
        }
        serializer = CatFactSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, data)
        
    def test_serializer_empty_fact_and_length(self):
        '''Verifies unsuccessful validation of CatFactSerializer with empty input'''
        data = {
            'fact': '',
            'length': ''  
        }
        serializer = CatFactSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('fact', serializer.errors)
        self.assertIn('length', serializer.errors)
        self.assertEqual(serializer.errors['fact'][0], "Fact cannot be Empty.")
        self.assertEqual(serializer.errors['length'][0], "A valid integer is required.")
    
    def test_serializer_empty_data_fact_validlength(self):
        '''Verifies unsuccessful validation of CatFactSerializer with empty fact and valid length'''
        invalid_data = {
            'fact': '',
            'length': self.fake.random_int()
        }
        serializer = CatFactSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('fact', serializer.errors) 
        self.assertEqual(serializer.errors['fact'][0], "Fact cannot be Empty.")
    
    def test_serializer_non_positive_length(self):
        '''Verifies unsuccessful validation of CatFactSerializer with valid url and negative length'''
        invalid_data = {
            'fact': self.fake.sentence(nb_words=15),
            'length':-55
        }
        serializer = CatFactSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('length', serializer.errors)
        self.assertEqual(serializer.errors['length'][0], "Length must be a positive integer.") 

class FetchCatFactViewTest(APITestCase):
   
    # def test_add_facts_with_create_batch(self):
    #     """Test FetchCatFactView with 10 different data instances using create_batch."""
    #     with self.settings(FETCH_URL="catfacts", FETCH_FLAG=True):
    #         self.assertIsInstance(settings.FETCH_URL, str)
    #         self.assertIsInstance(settings.FETCH_FLAG, bool)
    #         mock_data = CatFactFactory.create_batch(10)
    #         def mock_json_side_effect():
    #             if mock_data:
    #                 return mock_data.pop(0)
    #             return None
    #         with patch('requests.get') as mock_get:
    #             mock_get.return_value = MagicMock(
    #                 status_code=200,
    #                 json=mock_json_side_effect
    #             )
    #             result = FetchCatFactView.add_facts()
    #             saved_facts = CatFact.objects.all()
    #             self.assertEqual(saved_facts.count(), 10) 
    #             self.assertEqual(len(result), 10)         
    #             # Validate each fact is saved correctly
    #             for saved_fact, expected_fact in zip(saved_facts, result):
    #                 self.assertEqual(saved_fact.fact, expected_fact['fact'])
    #                 self.assertEqual(saved_fact.length, expected_fact['length'])    
    
    def test_add_facts_with_generator(self):
        """Test FetchCatFactView with 10 different data instances using a generator."""
        with self.settings(FETCH_URL="catfacts", FETCH_FLAG=True):
            self.assertIsInstance(settings.FETCH_URL, str)
            self.assertIsInstance(settings.FETCH_FLAG, bool)

            # Generator to yield 10 mock data entries
            def mock_data_generator():
                for _ in range(10):
                    yield CatFactFactory()
            mock_data_list = list(mock_data_generator())
            print("\nGenerated Mock Data:")
            for data in mock_data_list:
                print(data)
            
            def mock_json_side_effect():
                if mock_data_list:
                    return mock_data_list.pop(0)
                return None

            with patch('requests.get') as mock_get:
                mock_get.return_value = MagicMock(
                    status_code=200,
                    json=mock_json_side_effect
                )
                result = FetchCatFactView.add_facts()
                saved_facts = CatFact.objects.all()
                self.assertEqual(saved_facts.count(), 10)  
                self.assertEqual(len(result), 10)     
                for saved_fact, expected_fact in zip(saved_facts, result):
                    self.assertEqual(saved_fact.fact, expected_fact['fact'])
                    self.assertEqual(saved_fact.length, expected_fact['length'])
    
    
    def test_invalid_fetch_settings(self):
        '''Verifies error message response of FetchCatFactView on absence FETCH_URL and FETCH_FLAG'''
        error = "FETCH_URL and FETCH_FLAG must be valid"
        test_cases = [
        {"FETCH_URL": "ht5656we", "FETCH_FLAG": False},
        {"FETCH_URL": None, "FETCH_FLAG": True},
        {"FETCH_URL": "ht5656we.", "FETCH_FLAG": None},
        {"FETCH_URL": "ht5656we.", "FETCH_FLAG": []},
        {"FETCH_URL": "ht5656we.", "FETCH_FLAG":0},
        {"FETCH_URL": "ht5656we.", "FETCH_FLAG":''}, 
         {"FETCH_URL": "ht5656we.", "FETCH_FLAG":{}}, 
        ]
        for case in test_cases:
            with self.subTest(case=case):
                with self.settings(FETCH_URL=case["FETCH_URL"], FETCH_FLAG=case["FETCH_FLAG"]):
                    with self.assertRaises(ImproperlyConfigured) as cm:
                        FetchCatFactView.add_facts()
                    self.assertEqual(str(cm.exception), error)
                    
    def test_invalid_bool_string_settings(self):
        '''Verifies error message response of FetchCatFactView on invalid FETCH_URL and FETCH_FLAG'''
        error = "FETCH_URL must be a string and FETCH_FLAG must be a boolean"
        test_cases = [
        {"FETCH_URL": "ht5656we", "FETCH_FLAG": "false"},
        {"FETCH_URL": 345, "FETCH_FLAG": True},
        ]
        for case in test_cases:
            with self.subTest(case=case):
                with self.settings(FETCH_URL=case["FETCH_URL"], FETCH_FLAG=case["FETCH_FLAG"]):
                    with self.assertRaises(ImproperlyConfigured) as cm:
                        FetchCatFactView.add_facts()
                    self.assertEqual(str(cm.exception), error)
                    
    def test_http_error_handling(self):
        '''Verifies error message response on 404 Not Found error'''
        with self.settings(FETCH_URL="url", FETCH_FLAG=True):
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
        '''Verifies error message response on Network error'''
        with self.settings(FETCH_URL="url", FETCH_FLAG=True):
            with patch('requests.get') as mock_get:
                # Mock a network error
                mock_get.side_effect = requests.exceptions.RequestException("Network Error")
                result = FetchCatFactView.add_facts()
                self.assertEqual(result, [])
                mock_get.assert_called()
                
    def test_unexpected_error_handling(self):
        '''Verifies error message response on Unexpected error'''
        with self.settings(FETCH_URL="url", FETCH_FLAG=True):
            with patch('requests.get') as mock_get:
                # Mock an unexpected exception
                mock_get.side_effect = Exception("Unexpected Error")
                result = FetchCatFactView.add_facts()
                self.assertEqual(result, [])  # No facts should be saved on error
                mock_get.assert_called()

