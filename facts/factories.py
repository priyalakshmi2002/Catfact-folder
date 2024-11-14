import factory
from .models import *

class CatFactFactory(factory.DictFactory):
    fact = factory.Faker('sentence', nb_words=15)
    length = factory.Faker('random_int', min=10, max=150)  

