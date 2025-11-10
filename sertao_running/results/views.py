import json
import re
from pathlib import Path

from django.conf import settings
from django.shortcuts import render


def parse_results_file():
    file_path = Path(settings.BASE_DIR) / "results" / "data" / "presse.txt"
    text = file_path.read_text(encoding="utf-8")
    text = re.sub(r"<[^>]+>", " ", text)  # remove <a name="...">
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text)

    blocos = [b.strip() for b in text.split(";") if b.strip()]

    athletes = []
    for bloco in blocos:
        match = re.search(
            r"(\d+)[.)]?\s+([A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]+)\s+(\d+):(\d+):(\d+[.,]?\d*)\s*\(([^)]+)\)",
            bloco
        )
        if match:
            pos, name, h, m, s, team = match.groups()
            try:
                h, m, s = int(h), int(m), float(s.replace(",", "."))
                total_seconds = h * 3600 + m * 60 + s
                total_minutes = round(total_seconds / 60, 2)

                athletes.append({
                    "name": name.strip(),
                    "minutes": total_minutes,
                    "team": team.strip(),
                })
            except ValueError:
                continue

    athletes.sort(key=lambda x: x["minutes"])
    print(f"{len(athletes)} atletas encontrados.")
    return athletes




def chart_view(request):
    athletes = parse_results_file()

    labels = [a["name"] for a in athletes]
    data = [a["minutes"] for a in athletes]

    context = {
        # Envia como JSON pro template
        "labels_json": json.dumps(labels, ensure_ascii=False),
        "data_json": json.dumps(data),
    }
    return render(request, "results/chart.html", context)
