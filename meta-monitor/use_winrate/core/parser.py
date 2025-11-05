def analizar_fila(fila):
    """Procesa una fila <tr> y extrae datos de la carta."""
    try:
        nombre = fila.find_element("css selector", ".text-left.hidden.sm\\:block").text.strip()
        porcentajes = fila.find_elements("css selector", "div.text-3xl.font-bold")
        cambios = fila.find_elements("css selector", "div.text-sm.font-bold")

        uso = porcentajes[0].text.strip() if len(porcentajes) > 0 else ""
        winrate = porcentajes[1].text.strip() if len(porcentajes) > 1 else ""
        cambio_uso = cambios[0].text.strip() if len(cambios) > 0 else ""
        cambio_winrate = cambios[1].text.strip() if len(cambios) > 1 else ""

        tendencia_uso = "aumento" if "green" in cambios[0].get_attribute("class") else "disminución" if "red" in cambios[0].get_attribute("class") else "neutral"
        tendencia_winrate = "aumento" if "green" in cambios[1].get_attribute("class") else "disminución" if "red" in cambios[1].get_attribute("class") else "neutral"

        return {
            "nombre": nombre,
            "uso": uso,
            "cambio_uso": cambio_uso,
            "tendencia_uso": tendencia_uso,
            "winrate": winrate,
            "cambio_winrate": cambio_winrate,
            "tendencia_winrate": tendencia_winrate
        }
    except Exception:
        return None
