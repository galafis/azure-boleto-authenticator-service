"""Parser for Brazilian boleto bancario formats."""

import re
from datetime import date, timedelta
from typing import Optional

from .bank_codes import get_bank_name
from .models import BoletoInfo
from .validator import BoletoValidator

# Base date for calculating boleto due dates (07/10/1997)
BOLETO_BASE_DATE = date(1997, 10, 7)


class BoletoParser:
    """Parses Brazilian boleto bancario from linha digitavel or barcode formats.

    Supports:
        - 47-digit linha digitavel (typed line) format
        - 44-digit barcode format
    """

    @staticmethod
    def _clean_input(raw: str) -> str:
        """Remove non-numeric characters from input.

        Args:
            raw: Raw boleto string, possibly containing dots, spaces, etc.

        Returns:
            String containing only digits.
        """
        return re.sub(r"[^0-9]", "", raw)

    @staticmethod
    def linha_to_barcode(linha: str) -> str:
        """Convert a 47-digit linha digitavel to a 44-digit barcode.

        Linha digitavel structure:
            Field 1 (10 digits): AAABKCCCC.Dx  -> barcode[0:4] + barcode[19:24]
            Field 2 (11 digits): DDDDD.DDDDDy  -> barcode[24:34]
            Field 3 (11 digits): DDDDD.DDDDDz  -> barcode[34:44]
            Field 4 (1 digit):   V              -> barcode[4]
            Field 5 (14 digits): UUUUVVVVVVVVVV -> barcode[5:19]

        Args:
            linha: The 47-digit linha digitavel string.

        Returns:
            The corresponding 44-digit barcode string.
        """
        # Barcode positions:
        # [0:3]   = Bank code (linha[0:3])
        # [3]     = Currency code (linha[3])
        # [4]     = General check digit (linha[32])
        # [5:9]   = Due date factor (linha[33:37])
        # [9:19]  = Value (linha[37:47])
        # [19:24] = Free field part 1 (linha[4:9])
        # [24:34] = Free field part 2 (linha[10:20])
        # [34:44] = Free field part 3 (linha[21:31])

        barcode = (
            linha[0:4]       # Bank code + currency
            + linha[32]      # General check digit
            + linha[33:37]   # Due date factor
            + linha[37:47]   # Value
            + linha[4:9]     # Free field part 1
            + linha[10:20]   # Free field part 2
            + linha[21:31]   # Free field part 3
        )
        return barcode

    @staticmethod
    def barcode_to_linha(barcode: str) -> str:
        """Convert a 44-digit barcode to a 47-digit linha digitavel.

        Args:
            barcode: The 44-digit barcode string.

        Returns:
            The corresponding 47-digit linha digitavel string.
        """
        # Field 1: bank code + currency + free_field[0:5]
        field1_data = barcode[0:4] + barcode[19:24]
        field1_check = BoletoValidator.mod10(field1_data)
        field1 = field1_data + str(field1_check)

        # Field 2: free_field[5:15]
        field2_data = barcode[24:34]
        field2_check = BoletoValidator.mod10(field2_data)
        field2 = field2_data + str(field2_check)

        # Field 3: free_field[15:25]
        field3_data = barcode[34:44]
        field3_check = BoletoValidator.mod10(field3_data)
        field3 = field3_data + str(field3_check)

        # Field 4: general check digit
        field4 = barcode[4]

        # Field 5: due date factor + value
        field5 = barcode[5:19]

        return field1 + field2 + field3 + field4 + field5

    @staticmethod
    def _extract_due_date(factor_str: str) -> Optional[date]:
        """Extract the due date from the due date factor.

        The due date factor represents the number of days since 07/10/1997.
        A factor of '0000' means no due date is specified.

        Args:
            factor_str: The 4-digit due date factor string.

        Returns:
            The calculated due date, or None if factor is '0000'.
        """
        factor = int(factor_str)
        if factor == 0:
            return None
        return BOLETO_BASE_DATE + timedelta(days=factor)

    @staticmethod
    def _extract_value(value_str: str) -> float:
        """Extract the monetary value from the value field.

        The last two digits represent cents.

        Args:
            value_str: The 10-digit value string.

        Returns:
            The monetary value in BRL.
        """
        return int(value_str) / 100.0

    @classmethod
    def parse(cls, raw_input: str) -> BoletoInfo:
        """Parse a boleto from either linha digitavel or barcode format.

        Automatically detects the format based on the number of digits:
            - 47 digits: linha digitavel
            - 44 digits: barcode

        Args:
            raw_input: The raw boleto string (may contain formatting).

        Returns:
            A BoletoInfo object with parsed and validated information.
        """
        cleaned = cls._clean_input(raw_input)
        info = BoletoInfo()

        # Validate input length
        if len(cleaned) == 47:
            return cls._parse_linha_digitavel(cleaned)
        elif len(cleaned) == 44:
            return cls._parse_barcode(cleaned)
        else:
            info.errors.append(
                f"Formato invalido: esperados 44 ou 47 digitos, "
                f"encontrados {len(cleaned)}"
            )
            return info

    @classmethod
    def _parse_linha_digitavel(cls, linha: str) -> BoletoInfo:
        """Parse a 47-digit linha digitavel.

        Args:
            linha: The cleaned 47-digit string.

        Returns:
            A populated BoletoInfo object.
        """
        barcode = cls.linha_to_barcode(linha)

        info = BoletoInfo(
            bank_code=barcode[0:3],
            bank_name=get_bank_name(barcode[0:3]),
            currency_code=barcode[3],
            barcode=barcode,
            linha_digitavel=linha,
            free_field=barcode[19:44],
        )

        # Extract value and due date
        info.value = cls._extract_value(barcode[9:19])
        info.due_date = cls._extract_due_date(barcode[5:9])

        # Validate check digits
        is_valid, errors = BoletoValidator.validate_full(barcode, linha)
        info.valid = is_valid
        info.errors = errors

        return info

    @classmethod
    def _parse_barcode(cls, barcode: str) -> BoletoInfo:
        """Parse a 44-digit barcode.

        Args:
            barcode: The cleaned 44-digit string.

        Returns:
            A populated BoletoInfo object.
        """
        linha = cls.barcode_to_linha(barcode)

        info = BoletoInfo(
            bank_code=barcode[0:3],
            bank_name=get_bank_name(barcode[0:3]),
            currency_code=barcode[3],
            barcode=barcode,
            linha_digitavel=linha,
            free_field=barcode[19:44],
        )

        # Extract value and due date
        info.value = cls._extract_value(barcode[9:19])
        info.due_date = cls._extract_due_date(barcode[5:9])

        # Validate barcode check digit
        is_valid, errors = BoletoValidator.validate_barcode_check_digit(barcode)
        info.valid = is_valid
        info.errors = errors

        return info
