def formatar_moeda(valor: float) -> str:
    """Formata número no padrão brasileiro: R$ 1.234,56"""
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"
