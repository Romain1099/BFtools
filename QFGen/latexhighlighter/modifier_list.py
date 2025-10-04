
import re

def gras(texte=""):
	return f"\\textbf{{{texte}}}"

def multicols(texte="",nombre_colonnes=2)->str:
	texts=["",""]
	if re.search(r"\\columnbreak",texte):
		texts[0],texts[1]=texte.split(r"\\columnbreak",maxsplit=1)
		texte=f"{texts[0]}\n\n\\columnbreak\n\n{texts[1]}"
	elif re.search(r"%%",texte):
		texts[0],texts[1]=texte.split(r"%%",maxsplit=nombre_colonnes-1)
		texte=f"\t{texts[0]}\n\n\\columnbreak\n\n\t{texts[1]}"

	formatted_text = f"\\begin{{multicols}}{{{nombre_colonnes}}}\n{texte}\n\\end{{multicols}}"
	modified_text = f"\\vspace{{-0.25cm}}%\n{formatted_text}"
	return modified_text

def minipage(texte="",largeur="\\linewidth",type="t",fixed_height=False,height="",type_interne="c")->str:
	if fixed_height and height:
		formatted_text = f"\\begin{{minipage}}[{type}][{height}][{type_interne}]{{{largeur}}}\n\t{texte}\n\\end{{minipage}}"
	else:
		formatted_text = f"\\begin{{minipage}}[{type}][{type_interne}]{{{largeur}}}\n\t{texte}\n\\end{{minipage}}"
	return formatted_text

def double_minipage(texte:str="",largeur="0.45",unit:str="\\linewidth",type="t",fixed_height=False,height="",type_interne="c")->str:
	texts=["",""]
	if re.search(r"%%",texte):
		texts[0],texts[1]=texte.split(r"%%",maxsplit=1)
	else:
		texts[0]=texte
		texts[1]="\\phantom{a}\\\\"
	l_a = float(largeur)
	l_b = 1-l_a-0.05
	largeur_image=str(l_b)
	largeur_minipage_first=f"{largeur}{unit}"
	largeur_minipage_second=f"{largeur_image}{unit}"
	if fixed_height and height:
		formatted_text = f"\\hfill%\n\\begin{{minipage}}[{type}][{height}][{type_interne}]{{{largeur_minipage_first}}}\n\t{texts[0]}\n\\end{{minipage}}%\n\\hfill%\n\\begin{{minipage}}[{type}][{height}][{type_interne}]{{{largeur_minipage_second}}}\n\t{texts[1]}\n\\end{{minipage}}\\hfill"
	else:
		formatted_text = f"\\hfill%\n\\begin{{minipage}}[{type}]{{{largeur_minipage_first}}}\n\t{texts[0]}\n\\end{{minipage}}%\n\\hfill%\n\\begin{{minipage}}[{type}]{{{largeur_minipage_second}}}\n\t{texts[1]}\n\\end{{minipage}}\\hfill"
	return formatted_text

def image_insertion(texte="",image_path:str = "title.png",largeur:str = "0.45",unit="\\linewidth",centering:bool = True,image_dir:str="",legende:str="",minipage_option=False)->str:
	final_path = f"{image_dir}/{image_path}" if image_dir else image_path
	
	if legende:
		formatted_text=f"\\includegraphics[width = {largeur}{unit}]{{{final_path}}}\n\\captionof{{{legende}}}"
	else:
		formatted_text=f"\\includegraphics[width = {largeur}{unit}]{{{final_path}}}"
	if minipage_option==True:
		formatted_text=f"\\phantom{{a}}\\\\\n{formatted_text}"
	if centering:
		formatted_text=f"\\begin{{center}}\n\t{formatted_text}\n\\end{{center}}"
	if texte:
		formatted_text=f"{texte}\n{formatted_text}"
	return formatted_text	

def add_image_column(texte:str="",image_path:str = "title.png",image_dir:str="",legende:str="",largeur_texte:str="0.45",unit:str="\\linewidth",type="t",fixed_height=False,height="",type_interne="c")->str:
	l_a = float(largeur_texte)
	l_b = 1-l_a-0.05
	largeur_image=str(l_b)
	largeur_minipage_first=f"{largeur_texte}{unit}"
	largeur_minipage_second=f"{largeur_image}{unit}"
	image_text=image_insertion(image_path=image_path,largeur=largeur_image,unit=unit,centering=True,legende=legende,minipage_option=True)
	if fixed_height and height:
		formatted_text = f"\\hfill%\n\\begin{{minipage}}[{type}]{{{largeur_minipage_first}}}\n\t{texte}\n\\end{{minipage}}%\n\\hfill%\n\\begin{{minipage}}[{type}][{height}]{{{largeur_minipage_second}}}\n\t{image_text}\n\\end{{minipage}}%\n\\hfill"
	else:
		formatted_text = f"\\hfill%\n\\begin{{minipage}}[{type}]{{{largeur_minipage_first}}}\n\t{texte}\n\\end{{minipage}}%\n\\hfill%\n\n\\begin{{minipage}}[{type}]{{{largeur_minipage_second}}}\n\t{image_text}\n\\end{{minipage}}%\n\\hfill"
	return formatted_text

def enumerate(texte:str="",start=1,height_between_items=1)->str:
	#texte.replace(r"%%","\\item")
	texte = re.sub(r"%%", r"\\item", texte)
	formatted_text = f"\\begin{{enumerate}}[start = {start},itemsep = {height_between_items}em]\n\t\\item {texte}\n\\end{{enumerate}}"
	modified_text = f"\\vspace{{0.25cm}}%\n{formatted_text}"
	return modified_text

def itemize(texte:str="",label="\\faPen",height_between_items=1)->str:
	#texte.replace(r"%%","\\item")
	texte = re.sub(r"%%", r"\\item", texte)
	formatted_text = f"\\begin{{itemize}}[label={label},itemsep = {height_between_items}em]\n\t\\item {texte}\n\\end{{itemize}}"
	modified_text = f"\\vspace{{0.25cm}}%\n{formatted_text}"
	return modified_text