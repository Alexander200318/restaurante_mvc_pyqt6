"""
Utilidades de formato para mostrar datos en UI
"""

def formatear_moneda(valor: float) -> str:
    """Formatear valor como moneda USD"""
    return f"${valor:,.2f}"

def formatear_fecha(fecha) -> str:
    """Formatear fecha para display"""
    if not fecha:
        return "—"
    return fecha.strftime("%d/%m/%Y %H:%M")

def formatear_fecha_corta(fecha) -> str:
    """Formatear fecha sin hora"""
    if not fecha:
        return "—"
    return fecha.strftime("%d/%m/%Y")

def formatear_hora(fecha) -> str:
    """Formatear solo hora"""
    if not fecha:
        return "—"
    return fecha.strftime("%H:%M")

def ahortar_texto(texto: str, max_len: int = 50) -> str:
    """Acortar texto si es muy largo"""
    if not texto:
        return "—"
    if len(texto) > max_len:
        return texto[:max_len-3] + "..."
    return texto
