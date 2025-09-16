import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from loadconfig import loadDefaultConfig

def getTimetable(config):

    cursos = config["cursos"]
    timetable_path = config["timetable_path"]

    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    dias_map = {"Lunes": "L","Martes": "M","Miércoles": "X","Jueves": "J",
                "Viernes": "V","Sábado": "S","Domingo": "D"}

    all_rows = []

    for entry in cursos:
        curso = entry["curso"]
        url = entry["url"]

        payload = {
            "js": "true",
            "_drupal_ajax": "1",
            "ajax_page_state[theme]": "usc_theme",
            "ajax_page_state[theme_token]": "",
            "ajax_page_state[libraries]": "eJxljdEOwiAMRX8I5JNILQ2rDmpoMcGv183NqHtqc87NvShyZdKA73vRdsJUHR6x2phJdxMzBKgwD2NUl0XyTPEDwj9wOtSohDMoua4Y94GtdUFK7c64jE5QM3k1MPIv4zv_BvotLQoQEhVGj9Lb1msTFVpn_Pp-QexqUg5YWobKDzCW-gQuVGnO"
        }

        r = requests.post(url, data=payload, headers=headers)
        data_json = r.json()

        html = None
        for block in data_json:
            if block.get("selector") == "#course-detail-controller":
                html = block["data"]
                break
        if html is None:
            continue

        soup = BeautifulSoup(html, "html.parser")

        for day in soup.select(".calendar-day"):
            dia = day.select_one(".calendar-day-header h3").get_text(strip=True)
            dia_abrev = dias_map.get(dia, dia[0].upper())

            for subject in day.select(".ml-academic-subject"):
                asignatura = subject.select_one("h3 a").get_text(strip=True)
                # Normalizar espacios múltiples
                asignatura = " ".join(asignatura.split())

                detalles = subject.select(".academic-subject-specs-list li")

                horas, grupos, aulas = [], [], []

                for d in detalles:
                    text = d.get_text(strip=True)
                    if "-" in text and ":" in text:
                        horas.append(text)
                    else:
                        if "Aula" in text:
                            g, a = text.split("Aula", 1)
                            # Remove "Grupo ", "/" and "_" from grupo
                            g = g.strip().replace("Grupo ", "").replace("/", "").replace("_", "")
                            grupos.append(g)
                            aulas.append("Aula " + a.strip())
                        else:
                            grupos.append(text.strip().replace("/", "").replace("_", ""))
                            aulas.append("")

                for h in horas:
                    start_str, end_str = h.split("-")
                    start = datetime.strptime(start_str, "%H:%M")
                    end = datetime.strptime(end_str, "%H:%M")

                    current = start
                    while current < end:
                        next_time = current + timedelta(hours=1)
                        code_slot = f"{dia_abrev}{current.strftime('%H')}"

                        if grupos:
                            for g, a in zip(grupos, aulas):
                                all_rows.append({
                                    "Curso": curso,
                                    "Slot": code_slot,
                                    "Asignatura": asignatura,
                                    "Grupo": g,
                                    "Aula": a,
                                    "Hora": f"{current.strftime('%H:%M')}-{next_time.strftime('%H:%M')}"
                                })
                        else:
                            all_rows.append({
                                "Curso": curso,
                                "Slot": code_slot,
                                "Asignatura": asignatura,
                                "Grupo": "",
                                "Aula": "",
                                "Hora": f"{current.strftime('%H:%M')}-{next_time.strftime('%H:%M')}"
                            })
                        current = next_time

    # Guardar en CSV con columna Codigo
    df = pd.DataFrame(all_rows)
    df.to_csv(timetable_path, index=False, encoding="utf-8-sig", sep=";")

    print(f"Guardado en {timetable_path} con {len(df)} filas.")

if __name__ == "__main__":
    config = loadDefaultConfig()
    getTimetable(config)
