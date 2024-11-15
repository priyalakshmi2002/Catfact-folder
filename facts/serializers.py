from rest_framework import serializers
from .models import CatFact

class CatFactSerializer(serializers.ModelSerializer):
   fact = serializers.CharField(max_length = 500)
   length = serializers.IntegerField()
   
   class Meta:
       model = CatFact
       fields = ['fact','length']
       
   def validate_fact(self, value):
        if not value:
            raise serializers.ValidationError("Fact cannot be Empty.")
        return value

   def validate_length(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("Length must be a positive integer.")
        return value