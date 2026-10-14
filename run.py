"""Ejecuta la extracción y, opcionalmente, la creación del formulario."""
import argparse

from horarios.loadconfig import loadDefaultConfig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-forms", action="store_true", help="Genera CSV y JSON sin abrir Google Forms")
    args = parser.parse_args()

    from horarios.getTimetable import getTimetable
    from horarios.createFormsData import createFormsData

    config = loadDefaultConfig()
    getTimetable(config)
    createFormsData(config)
    if not args.no_forms:
        from horarios.createForms import createForms
        createForms(config)


if __name__ == "__main__":
    main()
