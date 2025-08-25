from unidecode import unidecode
import json

arvore_do_conhecimento_txt = []
arvore_do_conhecimento: dict = {}


def decode(s) -> str:
	return unidecode(s).replace("_", " ").strip().lower()


with open("arvore_do_conhecimento.txt", "r") as fs:
	lines = fs.readlines()
	arvore_do_conhecimento_txt = [decode(line) for line in lines]

	for line in lines:
		if line[0] == '\t':
			continue

		arvore_do_conhecimento |= {decode(line): None}

	for i in range(4):
		parent = None
		for line in lines:
			if line[i+1] == '\t':
				continue

			if line[i] == '\t':
				arvore_do_conhecimento |= {decode(line): parent}

			else:
				parent = decode(line)

with open("arvore_do_conhecimento.json", "w") as fs:
	fs.write(json.dumps(arvore_do_conhecimento, indent=4))

with open("data_complete.json", "r") as fs:
	data = json.loads(fs.read())

print(f"{len(arvore_do_conhecimento)} áreas identificadas pelo CNPq.")

areas_inputadas: set = set()
for line in data:
	for area in line["areas"]:
		areas_inputadas.add(decode(area))

print(f"{len(areas_inputadas)} áreas cadastradas no Lattes, das quais {len({area for area in areas_inputadas if area not in arvore_do_conhecimento})} não são canônicas.")
with open("areas_fantasma.txt", "w") as fs:
	fs.writelines(list({area + "\n" for area in areas_inputadas if area not in arvore_do_conhecimento}))

