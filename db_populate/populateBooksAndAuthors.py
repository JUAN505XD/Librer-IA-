import requests
import json

with open('idiomas_codigos_cache.json', 'r') as file:
    idiomas_codigos = json.load(file)

#for idioma in idiomas_codigos.values():
    # test 1: iterate languages over Physics subject

#    request = requests.get(f'https://openlibrary.org/search.json?q=subject:F%C3%ADsica&language={idioma}&limit=5&fields=title,author_name,isbn')

#    print(request)
try:
    request = requests.get(f'https://openlibrary.org/search.json?q=subject:F%C3%ADsica&language={idiomas_codigos["Español"]}&limit=5&fields=title,author_name,isbn,publisher,first_publish_year')
    request.raise_for_status()

    response = request.json()

except requests.exceptions.RequestException as e:
    print(e)
except json.JSONDecodeError as e:
    print(e)

# Lista con cada libro como diccionario
resultados = response['docs']

for libro in resultados:
    for publisher in libro.get('publisher'):
        print(publisher)
    for author in libro.get('author_name'):
        print(author)
    print(libro.get('title'))
    print(libro.get('isbn')[0])
    print(libro.get('first_publish_year'))
