import os
import xml.dom.minidom as dom

IN_FOLDER = "legendas-raw"
OUT_FOLDER = "legendas-txt-genero"
# Pega todos os arquivos presentes na pasta
FILES = [f for f in os.listdir(IN_FOLDER) if os.path.isfile(os.path.join(IN_FOLDER, f))]

print(f"Found {len(FILES)} files")

# [Ref] stackoverflow.com/a/61021445/4824627
def innerText(node):
  out = []
  for cur in node.childNodes:
    if cur.nodeType == cur.TEXT_NODE:
      out.append(cur.nodeValue)
    elif cur.nodeType == cur.ELEMENT_NODE:
      out.append(innerText(cur))
  return "".join(out).strip()

count = 0
it = 0
to_remove = []
for in_file in FILES:
  it += 1
  if it % 500 == 0:
    print(f"Reading file '{in_file}' ({it} iterations; {count+1} good files)")
  in_path = os.path.join(IN_FOLDER, in_file)
  out_path = os.path.join(OUT_FOLDER, in_file)

  document = None
  try:
    document = dom.parse(in_path).documentElement
  except Exception as e:
    print(f"Expat error on file '{in_path}'")
  else:
    with open(out_path, "w", encoding="utf-8") as out_file:
      # Ignora legendas traduzidas automaticamente
      leave = False
      for mt in document.getElementsByTagName("machine_translated"):
        if innerText(mt) == "1":
          leave = True
          break

      if leave:
        to_remove.append(out_path)
        continue

      genres = []
      # Para toda tag <meta>
      for meta in document.getElementsByTagName("meta"):
        # Para toda tag <source>
        for source in meta.getElementsByTagName("source"):
          # Para toda tag <genre>
          for genre in meta.getElementsByTagName("genre"):
            # Pega lista de gêneros
            text = genre.firstChild.nodeValue
            # Adiciona cada um na lista "global"
            genres += text.split(',')
      # Escreve no arquivo
      genre_list = ";".join(genres)

      # Se tem menos de 100 "frases", não vamos usar essa
      subtitle_elements = document.getElementsByTagName("s")
      if len(subtitle_elements) < 100:
        to_remove.append(out_path)
        continue

      subtitles = []
      # Pega toda tag de legenda, <s>, entre as 20 primeiras e as 20 últimas
      # e adiciona o texto no arquivo final
      for subtitle in subtitle_elements[20:-20]:
        subtitles.append(innerText(subtitle))

      out_file.write(f"{genre_list}\n")
      _t = "\n".join(subtitles)
      out_file.write(f"{_t}")
      count += 1

# Remove arquivos criados erroneamente
for f in to_remove:
  os.remove(f)

print(f"Wrote {count} files")

## Exemplo de legenda: ##
#   <s id="35">
#     <time id="T40S" value="00:03:40,707" />
# Fracasso... pode significar morte.
#     <time id="T41E" value="00:03:46,620" />
#   </s>

## Exemplo de metadado: ##
# <meta>
#   <subtitle>
#     <duration>00:08:24,847</duration>
#     <language>Portuguese (BR)</language>
#     <rating>4.0</rating>
#     <version>0</version>
#     <confidence>1.0</confidence>
#     <blocks>30</blocks>
#     <machine_translated>0</machine_translated>
#     <date>2012-04-10</date>
#   </subtitle>
#   <conversion>
#     <unknown_words>4</unknown_words>
#     <encoding>windows-1252</encoding>
#     <sentences>33</sentences>
#     <corrected_words>1</corrected_words>
#     <ignored_blocks>2</ignored_blocks>
#     <truecased_words>4</truecased_words>
#     <tokens>133</tokens>
#   </conversion>
#   <source>
#     <original>English</original>
#     <year>2016</year>
#     <country>Italy</country>
#     <genre>Horror,Short</genre>
#     <duration>30</duration>
#     <HD>0</HD>
#     <cds>1/1</cds>
#   </source>
# </meta>