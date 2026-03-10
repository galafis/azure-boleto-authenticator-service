"""Data models for boleto information."""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class BoletoInfo:
    """Represents the parsed and validated information from a Brazilian boleto.

    Attributes:
        bank_code: The 3-digit bank identification code.
        bank_name: The name of the issuing bank.
        value: The monetary value of the boleto in BRL.
        due_date: The payment due date, if available.
        barcode: The 44-digit barcode representation.
        linha_digitavel: The 47-digit typed line representation.
        valid: Whether the boleto passed check digit validation.
        currency_code: The currency code (9 = BRL).
        free_field: The free field portion of the barcode.
        errors: List of validation error messages.
    """

    bank_code: str = ""
    bank_name: str = ""
    value: float = 0.0
    due_date: Optional[date] = None
    barcode: str = ""
    linha_digitavel: str = ""
    valid: bool = False
    currency_code: str = "9"
    free_field: str = ""
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert the BoletoInfo to a dictionary representation.

        Returns:
            Dictionary with all boleto information fields.
        """
        return {
            "bank_code": self.bank_code,
            "bank_name": self.bank_name,
            "value": self.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "barcode": self.barcode,
            "linha_digitavel": self.linha_digitavel,
            "valid": self.valid,
            "currency_code": self.currency_code,
            "free_field": self.free_field,
            "errors": self.errors,
        }

    def __str__(self) -> str:
        status = "Valido" if self.valid else "Invalido"
        due = self.due_date.strftime("%d/%m/%Y") if self.due_date else "N/A"
        return (
            f"Boleto [{status}]\n"
            f"  Banco: {self.bank_code} - {self.bank_name}\n"
            f"  Valor: R$ {self.value:,.2f}\n"
            f"  Vencimento: {due}\n"
            f"  Codigo de barras: {self.barcode}"
        )
