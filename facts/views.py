import requests
import logging
from .serializers import CatFactSerializer
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from requests.exceptions import HTTPError, RequestException

# Set up logging configuration
logger = logging.getLogger(__name__)

class FetchCatFactView:
    @classmethod
    def add_facts(self):
        logger.info("Fetching cat fact....")
        url = getattr(settings, "FETCH_URL", None)
        fetch_flag = getattr(settings, "FETCH_FLAG", None)
        if not (url and fetch_flag):
            raise ImproperlyConfigured("FETCH_URL and FETCH_FLAG must be valid")
        elif not isinstance(url, str) or not isinstance(fetch_flag, bool):
            raise ImproperlyConfigured("FETCH_URL must be a string and FETCH_FLAG must be a boolean")

        resultData = []
        for i in range(10):
            try:
                response = requests.get(url)
                response.raise_for_status() 
                data = response.json()
                serializer = CatFactSerializer(data=data)
                if serializer.is_valid():
                    logger.info(f"Serializer data is valid: {serializer.validated_data}")
                    serializer.save()
                    logger.info(f"CatFacts saved successfully: {serializer.validated_data}")
                    resultData.append(serializer.validated_data)
                else:
                    logger.error(f"Serializer validation failed: {serializer.errors}")
            except HTTPError as http_err:
                logger.error(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
            except RequestException as req_err:
                logger.error(f"Network-related error occurred: {req_err}")
            except Exception as err:
                logger.error(f"An unexpected error occurred: {err}")
        return resultData
         



  
        
        
        
        