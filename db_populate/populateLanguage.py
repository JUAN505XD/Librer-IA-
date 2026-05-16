import requests
from bs4 import BeautifulSoup

url = 'https://openlibrary.org/subjects'

headers = {'Accept-Language':'es-ES,es:q=0.9'}

cookies = {'lang':'es'}

response = requests.get(url, cookies = cookies, headers = headers)

soup = BeautifulSoup(response.text, 'html.parser')

materias = soup.find(id='subjectsPage')

idiomas=[]


for materia_principal in materias.find_all('h3'):
    if materia_principal.string == "Libros por idioma":
    # The first sibling is the newline, the second sibling is the actual next tag, the <ul> tag with its strings
        for idioma in materia_principal.next_sibling.next_sibling.stripped_strings:
            if idioma != "Ver más...":
                idiomas.append(idioma)

