from django.db import models

class CatFact(models.Model):
    fact = models.TextField()
    length = models.IntegerField()
    
    def __str__(self):
        return f"CatFact(fact={self.fact},length={self.length})" 