import os 
import requests
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from libros.models import Libro, Genero, Idioma, Autor, Editorial
from db_populate import utils

class Command(BaseCommand):
    help = 'Poblar la base de datos'

    def handle(self, *args, **kwargs):
        # Fase 1 
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

        # Fase 2 

        self.stdout.write("Fase 2: Autores, Editoriales y Libros")

        path_idiomas_codigos=os.path.join(settings.BASE_DIR,'db_populate','cache','idiomas_codigos_cache.json')

        #Idiomas mapped with their codes (Ej: Español:esp)
        with open(path_idiomas_codigos,'r',encoding='utf-8') as f_idiomas_codigos:
            idiomas_codigos = json.load(f_idiomas_codigos)

        subject='Física'

        try:
            headers = {
                    "User-Agent": "LibrerIA (juan.henao6@utp.edu.co)"
                    }

            request = requests.get(f'https://openlibrary.org/search.json?q=subject:{subject}&language={idiomas_codigos["Español"]}&limit=5&fields=title,author_name,isbn,publisher,first_publish_year',headers=headers)

            request.raise_for_status()

            response = request.json()

        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f"{e}"))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"{e}"))
            return

        # Lista con cada libro como diccionario

        resultados = response.get('docs',[])

        libros_creados = 0

        for libro in resultados:
            isbnsLibro = libro.get('isbn', [])
            isbnLibro = isbnsLibro[0] if isbnsLibro else '?'

            if isbnLibro == '?':
                continue
 
            titulo = libro.get('title', '?')
            año_publicacion= libro.get('first_publish_year')

            genero_obj,_ = Genero.objects.get_or_create(nombre=subject.strip())

            idioma_obj,_ = Idioma.objects.get_or_create(nombre='Español')
            
            autoresLibro = libro.get('author_name', [])
            autores=[]
            
            editorialesLibro = libro.get('publisher', [])
            editorialLibro = editorialesLibro[0] if editorialesLibro else '?'
            editorial_obj, _ = Editorial.objects.get_or_create(nombre=editorialLibro.strip())
            
            
            for autor in autoresLibro:
                autor_obj, _ = Autor.objects.get_or_create(nombre=autor.strip())
                autores.append(autor_obj)
            
            for editorialAdicional in editorialesLibro:
                editorialAdicional_obj, _ = Editorial.objects.get_or_create(nombre=editorialAdicional.strip())

           
            paginas = utils.generar_paginas()

            precio = utils.generar_precio(paginas)

            estado = utils.generar_estado(precio)

            libro_obj, creado = Libro.objects.get_or_create(
                    issn=isbnLibro,
                    defaults={
                        'titulo':titulo,
                        'editorial':editorial_obj,
                        'genero':genero_obj,
                        'idioma':idioma_obj,
                        'numero_paginas':paginas,
                        'año_publicacion':año_publicacion,
                        'estado':estado,
                        'precio':precio
                        }
                    )

            libro_obj.autores.add(*autores)

            if creado:
                libros_creados+=1
                self.stdout.write(f"Guardado {titulo}")
            else:
                self.stdout.write(f"Ya existia {titulo}")

        self.stdout.write(self.style.SUCCESS(f"\nSe insertaron {libros_creados} libros nuevos"))
