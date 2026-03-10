"""Mapping of Brazilian bank codes to their names."""

BANK_CODES: dict[str, str] = {
    "001": "Banco do Brasil",
    "003": "Banco da Amazonia",
    "004": "Banco do Nordeste",
    "021": "Banestes",
    "033": "Santander",
    "036": "Bradesco BBI",
    "041": "Banrisul",
    "047": "Banese",
    "070": "BRB",
    "077": "Banco Inter",
    "104": "Caixa Economica Federal",
    "136": "Unicred",
    "197": "Stone Pagamentos",
    "208": "BTG Pactual",
    "212": "Banco Original",
    "237": "Bradesco",
    "246": "ABC Brasil",
    "260": "Nubank",
    "269": "HSBC",
    "290": "Pagseguro",
    "318": "BMG",
    "336": "C6 Bank",
    "341": "Itau Unibanco",
    "356": "ABN Amro Real",
    "389": "Mercantil do Brasil",
    "399": "HSBC Bank Brasil",
    "422": "Safra",
    "453": "Rural",
    "633": "Rendimento",
    "652": "Itau Unibanco Holding",
    "707": "Daycoval",
    "745": "Citibank",
    "748": "Sicredi",
    "756": "Sicoob",
}


def get_bank_name(code: str) -> str:
    """Return the bank name for a given bank code.

    Args:
        code: The 3-digit bank code string.

    Returns:
        The bank name, or 'Desconhecido' if the code is not found.
    """
    return BANK_CODES.get(code, "Desconhecido")
