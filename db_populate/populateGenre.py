import requests
from bs4 import BeautifulSoup

url = 'https://openlibrary.org/subjects'

headers = {'Accept-Language':'es-ES,es:q=0.9'}

cookies = {'lang':'es'}

response = requests.get(url, cookies = cookies, headers = headers)

soup = BeautifulSoup(response.text, 'html.parser')

materias = soup.find(id='subjectsPage')

generos=[]

for materia_principal in materias.find_all('h3'):
    if materia_principal.string != "Libros por idioma":
        generos.append(materia_principal.string)
        # First next sibling is the newline \n, the next one is the actual tag <ul>
        for sub_materia in materia_principal.next_sibling.next_sibling.stripped_strings:
            generos.append(sub_materia)

