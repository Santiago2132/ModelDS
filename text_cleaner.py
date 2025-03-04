import re

def clean_text(text):
    # Expresión regular para eliminar palabras en otros idiomas (no español)
    # Esta es una lista básica de caracteres comunes en otros idiomas, puedes ampliarla
    non_spanish_pattern = re.compile(r'\b[a-zA-Z]*[^a-zA-ZáéíóúñÁÉÍÓÚÑ\s][a-zA-Z]*\b')
    
    # Eliminar palabras que no estén en español
    cleaned_text = non_spanish_pattern.sub('', text)
    
    # Eliminar espacios extras y retornar el texto limpio
    return ' '.join(cleaned_text.split())