import pandas as pd
import json
from loadconfig import loadDefaultConfig

def sort_custom(keys):
    def key_func(k):
        # Split prefix and number
        prefix = ''.join(filter(str.isalpha, k))
        number = int(''.join(filter(str.isdigit, k)))
        # Define the order of prefixes
        prefix_order = {'CLE': 0, 'CLIS': 1, 'CLIL': 2}
        return (prefix_order.get(prefix, 99), number)
    
    return sorted(keys, key=key_func)

def createFormsData(config):

    timetable_path = config["timetable_path"]
    forms_data_path = config["forms_data_path"]
    # Read CSV
    df = pd.read_csv(timetable_path, sep=';')

    # Get unique cursos in order
    cursos = df['Curso'].drop_duplicates().tolist()

    # Initialize dictionary
    dic = {}

    for curso in cursos:
        df_curso = df[df['Curso'] == curso]
        asignaturas = df_curso['Asignatura'].drop_duplicates().tolist()
        dic[curso] = {}
        for asignatura in asignaturas:
            grupos = df_curso[df_curso['Asignatura'] == asignatura]['Grupo'].drop_duplicates().tolist()
            dic[curso][asignatura] = sort_custom(grupos)

    with open(forms_data_path, 'w', encoding='utf-8') as f:
        json.dump(dic, f, ensure_ascii=False, indent=4)
    print(f"Data para el forms guardada en {forms_data_path}.")
    return dic


if __name__ == "__main__":
    config = loadDefaultConfig()
    dic = createFormsData(config)
