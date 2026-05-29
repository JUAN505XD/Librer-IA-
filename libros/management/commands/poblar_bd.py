import os 
import requests
import json
import random # 🔥 Agregado para el sampleo de idiomas
from django.core.management.base import BaseCommand
from django.conf import settings
from libros.models import Libro, Genero, Idioma, Autor, Editorial
from db_populate import utils
from datetime import date

class Command(BaseCommand):
    help = 'Poblar la base de datos'

    def handle(self, *args, **kwargs):
        # =========================================================================
        # FASE 1: Carga Básica e Inserción Inicial de Idiomas y Géneros
        # =========================================================================
        self.stdout.write("Fase 1: Idiomas y Géneros")

        path_generos = os.path.join(settings.BASE_DIR, 'db_populate', 'cache', 'generos_cache.json')
        path_idiomas = os.path.join(settings.BASE_DIR, 'db_populate', 'cache', 'idiomas_cache.json')
        path_idiomas_codigos = os.path.join(settings.BASE_DIR, 'db_populate', 'cache', 'idiomas_codigos_cache.json')

        with open(path_generos, 'r', encoding='utf-8') as f_generos, \
             open(path_idiomas, 'r', encoding='utf-8') as f_idiomas, \
             open(path_idiomas_codigos, 'r', encoding='utf-8') as f_idiomas_codigos:
            
            generos = json.load(f_generos)
            idiomas = json.load(f_idiomas)
            idiomas_codigos = json.load(f_idiomas_codigos)

            # Población masiva inicial en la DB
            for genero in generos:
                Genero.objects.get_or_create(nombre=genero.strip())
            for idioma in idiomas:
                Idioma.objects.get_or_create(nombre=idioma.strip())

            self.stdout.write(self.style.SUCCESS("Idiomas y Géneros poblados iniciales con éxito"))

            # =========================================================================
            # FASE 2: Autores, Editoriales y Libros (Anidado debajo para reusar los archivos)
            # =========================================================================
            self.stdout.write("Fase 2: Autores, Editoriales y Libros mediante OpenLibrary")
            
            libros_creados = 0
            headers = {
                "User-Agent": "LibrerIA (juan.henao6@utp.edu.co)"
            }

            # 🔄 1. Iteramos por los 98 géneros cargados en la Fase 1
            for subject in generos:
                subject_clean = subject.strip()
                genero_obj, _ = Genero.objects.get_or_create(nombre=subject_clean)

                # 🎲 2. Elegimos 5 nombres de idiomas aleatorios únicos de la lista de idiomas_cache
                idiomas_seleccionados = random.sample(idiomas, 5)

                # 🔄 3. Iteramos por los 5 idiomas seleccionados
                for idioma_nombre in idiomas_seleccionados:
                    idioma_nombre_clean = idioma_nombre.strip()
                    
                    # Obtenemos el código de la API (Ej: "Español" -> "esp") desde el diccionario
                    codigo_api = idiomas_codigos.get(idioma_nombre_clean)
                    if not codigo_api:
                        continue # Seguridad por si algún nombre no mapea con su código

                    idioma_obj, _ = Idioma.objects.get_or_create(nombre=idioma_nombre_clean)
                    
                    self.stdout.write(f"Solicitando OpenLibrary -> Género: '{subject_clean}' | Idioma: '{idioma_nombre_clean}'")

                    # Ejecución del Request HTTP adaptado a las variables del bucle actual
                    try:
                        url_api = f'https://openlibrary.org/search.json?q=subject:{subject_clean}&language={codigo_api}&limit=5&fields=title,author_name,isbn,publisher,first_publish_year'
                        request = requests.get(url_api, headers=headers)
                        request.raise_for_status()
                        response = request.json()
                    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                        # Si una petición falla, la reportamos pero continuamos con el siguiente idioma/género
                        self.stdout.write(self.style.WARNING(f"Error al consultar API para {subject_clean} [{codigo_api}]: {e}"))
                        continue

                    resultados = response.get('docs', [])

                    # Procesamos los 5 libros devueltos por la API para esta combinación
                    for libro in resultados:
                        isbnsLibro = libro.get('isbn', [])
                        isbnLibro = isbnsLibro[0] if isbnsLibro else '?'

                        if isbnLibro == '?':
                            continue

                        titulo = libro.get('title', '?')
                        año_publicacion = libro.get('first_publish_year') or date.today().year

                        autoresLibro = libro.get('author_name', [])
                        autores = []
                        
                        editorialesLibro = libro.get('publisher', [])
                        editorialLibro = editorialesLibro[0] if editorialesLibro else '?'
                        editorial_obj, _ = Editorial.objects.get_or_create(nombre=editorialLibro.strip())
                        
                        # Poblar autores individuales
                        for autor in autoresLibro:
                            autor_obj, _ = Autor.objects.get_or_create(nombre=autor.strip())
                            autores.append(autor_obj)
                        
                        # Poblar editoriales adicionales (manteniendo tu lógica original)
                        for editorialAdicional in editorialesLibro:
                            Editorial.objects.get_or_create(nombre=editorialAdicional.strip())

                        # Cálculos y utilidades (El precio ya viene validado por tus utils)
                        paginas = utils.generar_paginas()
                        precio = utils.generar_precio(paginas)
                        estado = utils.generar_estado(precio)

                        # Inserción del Libro
                        libro_obj, creado = Libro.objects.get_or_create(
                            issn=isbnLibro,
                            defaults={
                                'titulo': titulo,
                                'editorial': editorial_obj,
                                'genero': genero_obj,
                                'idioma': idioma_obj,
                                'numero_paginas': paginas,
                                'año_publicacion': año_publicacion,
                                'estado': estado,
                                'precio': precio
                            }
                        )

                        # Guardamos la relación ManyToMany de Autores
                        libro_obj.autores.add(*autores)

                        if creado:
                            libros_creados += 1
                            self.stdout.write(f"   -> Guardado: {titulo}")
                        else:
                            self.stdout.write(f"   -> Ya existía: {titulo}")

        self.stdout.write(self.style.SUCCESS(f"\nProceso finalizado. Se insertaron {libros_creados} libros nuevos."))
