"""Demo script for the Brazilian Boleto Authenticator Service.

Demonstrates parsing and validating boleto bancario payment slips
in both linha digitavel (47-digit) and barcode (44-digit) formats.
"""

from src.boleto.parser import BoletoParser
from src.boleto.bank_codes import BANK_CODES


def print_separator() -> None:
    """Print a visual separator line."""
    print("=" * 60)


def demo_bank_codes() -> None:
    """Display all supported bank codes."""
    print_separator()
    print("SUPPORTED BANK CODES")
    print_separator()
    for code, name in sorted(BANK_CODES.items()):
        print(f"  {code} - {name}")
    print()


def demo_parse_boletos() -> None:
    """Demonstrate boleto parsing with sample data."""
    print_separator()
    print("BOLETO PARSING DEMO")
    print_separator()

    # Sample boletos for demonstration
    # Note: These are constructed examples for demonstration purposes.
    samples = [
        {
            "label": "Banco do Brasil - Linha Digitavel",
            "input": "00190.50095 40144.816069 06809.350314 3 37370000000100",
        },
        {
            "label": "Itau - Linha Digitavel",
            "input": "34191.75124 34567.861230 41234.560005 1 84340000019990",
        },
        {
            "label": "Bradesco - Barcode (44 digits)",
            "input": "23793381300000150001234560000012345678901016",
        },
    ]

    for sample in samples:
        print(f"\nInput: {sample['label']}")
        print(f"  Raw: {sample['input']}")

        result = BoletoParser.parse(sample["input"])
        print(f"  {result}")

        if not result.valid:
            for error in result.errors:
                print(f"  Erro: {error}")
        print()


def demo_format_conversion() -> None:
    """Demonstrate conversion between linha digitavel and barcode formats."""
    print_separator()
    print("FORMAT CONVERSION DEMO")
    print_separator()

    linha = "00190500954014481606906809350314337370000000100"
    barcode = BoletoParser.linha_to_barcode(linha)
    print(f"  Linha digitavel: {linha}")
    print(f"  Barcode:         {barcode}")

    reconverted = BoletoParser.barcode_to_linha(barcode)
    print(f"  Reconverted:     {reconverted}")
    print(f"  Match: {linha == reconverted}")
    print()


def main() -> None:
    """Run all demo functions."""
    print("\n  BRAZILIAN BOLETO AUTHENTICATOR SERVICE")
    print("  Servico de Autenticacao de Boletos Brasileiros\n")

    demo_bank_codes()
    demo_parse_boletos()
    demo_format_conversion()

    print_separator()
    print("Demo complete / Demo concluida")
    print_separator()


if __name__ == "__main__":
    main()
