import json 

with open('idiomas_cache.json') as idiomas_file:
    idiomas = json.load(idiomas_file)

codigos = ['eng', 'fre', 'spa', 'ger', 'rus', 'ita', 'chi', 'jpn']

idiomas_codigos = dict(zip(idiomas,codigos))


with open('idiomas_codigos_cache.json', 'w') as idiomas_codigos_file:
          json.dump(idiomas_codigos, idiomas_codigos_file)
