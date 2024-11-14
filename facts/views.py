import requests
import logging
from .serializers import CatFactSerializer
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

# Set up logging configuration
logger = logging.getLogger(__name__)

class FetchCatFactView:
    @classmethod
    def add_facts(self):
        logger.info("Fetching cat fact....")
        # url to be a string
        url = settings.FETCH_URL
        if not isinstance(url, str):
            raise ImproperlyConfigured("FETCH_URL must be a string")
        
        #flag to be a boolean value
        flag = settings.FETCH_FLAG
        if not isinstance(flag, bool):
            raise ImproperlyConfigured("FETCH_FLAG must be a boolean")
        
        #flag as false
        if not flag:
            logger.info("Fetch is disabled in settings")
            return []
        
        resultData = []
        for i in range(10):
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                serializer = CatFactSerializer(data=data)
                if serializer.is_valid():
                    logger.info(f"Serializer data is valid: {serializer.validated_data}")
                    serializer.save()
                    logger.info(f"CatFacts saved successfully: {serializer.validated_data}")
                    resultData.append(serializer.validated_data)     
                else:
                    logger.error(f"Serializer validation failed: {serializer.errors}")
            else:
                logger.error(f"Failed to fetch data from API.Status code: {response.status_code}")
        return resultData
         
         



  
        
        
        
        