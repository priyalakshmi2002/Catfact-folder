from rest_framework import serializers
from .models import CatFact

class CatFactSerializer(serializers.ModelSerializer):
        
    fact = serializers.CharField(max_length=500, required=True, allow_blank=True)  
    length = serializers.IntegerField(required=True)
    class Meta:
       model = CatFact
       fields = ['fact','length']
       
    def validate_fact(self, value):
        if not value:
            raise serializers.ValidationError("Fact cannot be Empty.")
        return value

    def validate_length(self, value):
        if not isinstance(value,int):
            raise serializers.ValidationError("Length must be a valid integer")
        if value is None or value <= 0:
            raise serializers.ValidationError("Length must be a positive integer.")
        return value