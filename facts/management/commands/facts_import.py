import requests
from django.core.management.base import BaseCommand
from facts.models import CatFact
from facts.views import FetchCatFactView

class Command(BaseCommand):
    help = 'Import cat facts from the external API and save them to the CatFact model.'

    def handle(self, *args, **kwargs):

        facts_data = FetchCatFactView.add_facts()
        if facts_data:
            self.stdout.write(self.style.SUCCESS(f"Successfully imported fact: {len(facts_data)}"))
        # else:
        #     self.stdout.write(self.style.WARNING("No fact available in the response."))

    