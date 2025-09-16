from loadconfig import loadDefaultConfig
from getTimetable import getTimetable
from createFormsData import createFormsData
from createForms import createForms

wantToCreateForms = True

if __name__ == "__main__":
    config = loadDefaultConfig()
    print("Config loaded.")
    getTimetable(config)
    createFormsData(config)
    if wantToCreateForms:
        createForms(config)
