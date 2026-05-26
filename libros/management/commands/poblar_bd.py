import os 
import requests
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from libros.models import Libro, Genero, Idioma, Autor, Editorial

class Command(BaseCommand):
    help = 'Poblar la base de datos'

    def handle(self, *args, **kwargs):
        self.stdout.write("Fase 1: Idiomas y Géneros")

        path_generos=os.path.join(settings.BASE_DIR,'db_populate','cache','generos_cache.json')
        path_idiomas=os.path.join(settings.BASE_DIR,'db_populate','cache','idiomas_cache.json')

        with open(path_generos,'r',encoding='utf-8') as f_generos,open(path_idiomas,'r',encoding='utf-8') as f_idiomas:
            generos=json.load(f_generos)
            idiomas=json.load(f_idiomas)

            for genero in generos:
                Genero.objects.get_or_create(nombre=genero.strip())
            for idioma in idiomas:
                Idioma.objects.get_or_create(nombre=idioma.strip())

        self.stdout.write(self.style.SUCCESS("Idiomas y Géneros poblados con éxito"))

#with open('cache/idiomas_codigos_cache.json', 'r') as file:
#    idiomas_codigos = json.load(file)

#for idioma in idiomas_codigos.values():
    # test 1: iterate languages over Physics subject

#    request = requests.get(f'https://openlibrary.org/search.json?q=subject:F%C3%ADsica&language={idioma}&limit=5&fields=title,author_name,isbn')

#    print(request)
#try:
#    headers = {
#            "User-Agent": "LibrerIA (juan.henao6@utp.edu.co)"
#    }
#
#    request = requests.get(f'https://openlibrary.org/search.json?q=subject:F%C3%ADsica&language={idiomas_codigos["Español"]}&limit=5&fields=title,author_name,isbn,publisher,first_publish_year', headers=headers)
    
#    request.raise_for_status()

#    response = request.json()

#except requests.exceptions.RequestException as e:
#    print(e)
#except json.JSONDecodeError as e:
#    print(e)

# Lista con cada libro como diccionario
#resultados = response['docs']

#for libro in resultados:
#    for publisher in libro.get('publisher'):
#        print(publisher)
#    for author in libro.get('author_name'):
#        print(author)
#    print(libro.get('title'))
#    print(libro.get('isbn')[0])
#    print(libro.get('first_publish_year'))
