"""Check digit validation algorithms for Brazilian boletos."""


class BoletoValidator:
    """Validates Brazilian boleto check digits using Mod10 and Mod11 algorithms."""

    @staticmethod
    def mod10(number: str) -> int:
        """Calculate Mod10 check digit (Luhn-like algorithm).

        Used for validating fields 1, 2, and 3 of the linha digitavel.
        Multiplies each digit alternately by 2 and 1 (right to left),
        sums the individual digits of the products, and returns
        the complement to the next multiple of 10.

        Args:
            number: The numeric string to calculate the check digit for.

        Returns:
            The Mod10 check digit (0-9).
        """
        total = 0
        weight = 2

        for digit in reversed(number):
            product = int(digit) * weight
            # Sum individual digits of product (e.g., 14 -> 1 + 4 = 5)
            total += product // 10 + product % 10
            weight = 3 - weight  # Alternate between 2 and 1

        remainder = total % 10
        return 0 if remainder == 0 else 10 - remainder

    @staticmethod
    def mod11(number: str, base: int = 9) -> int:
        """Calculate Mod11 check digit.

        Used for validating the general check digit (position 5 of barcode).
        Multiplies each digit by weights cycling from 2 to `base` (right to left),
        sums the products, and returns the check digit based on the remainder.

        Args:
            number: The numeric string to calculate the check digit for.
            base: The maximum weight value (default 9 for boleto bancario).

        Returns:
            The Mod11 check digit. Returns 1 if the calculated digit
            is 0, 10, or 11.
        """
        total = 0
        weight = 2

        for digit in reversed(number):
            total += int(digit) * weight
            weight += 1
            if weight > base:
                weight = 2

        remainder = total % 11
        check = 11 - remainder

        if check in (0, 10, 11):
            return 1
        return check

    @classmethod
    def validate_linha_digitavel_fields(cls, linha: str) -> tuple[bool, list[str]]:
        """Validate the three Mod10 check digits in the linha digitavel.

        The linha digitavel (47 digits) has three fields, each with a
        Mod10 check digit:
          - Field 1: positions 0-8 (data), position 9 (check digit)
          - Field 2: positions 10-19 (data), position 20 (check digit)
          - Field 3: positions 21-30 (data), position 31 (check digit)

        Args:
            linha: The 47-digit linha digitavel string.

        Returns:
            A tuple of (is_valid, errors) where is_valid indicates whether
            all check digits are correct.
        """
        errors = []

        # Field 1: digits 0-8 checked against digit 9
        field1_data = linha[0:9]
        field1_check = int(linha[9])
        calculated1 = cls.mod10(field1_data)
        if field1_check != calculated1:
            errors.append(
                f"Campo 1: digito verificador invalido "
                f"(esperado {calculated1}, encontrado {field1_check})"
            )

        # Field 2: digits 10-19 checked against digit 20
        field2_data = linha[10:20]
        field2_check = int(linha[20])
        calculated2 = cls.mod10(field2_data)
        if field2_check != calculated2:
            errors.append(
                f"Campo 2: digito verificador invalido "
                f"(esperado {calculated2}, encontrado {field2_check})"
            )

        # Field 3: digits 21-30 checked against digit 31
        field3_data = linha[21:31]
        field3_check = int(linha[31])
        calculated3 = cls.mod10(field3_data)
        if field3_check != calculated3:
            errors.append(
                f"Campo 3: digito verificador invalido "
                f"(esperado {calculated3}, encontrado {field3_check})"
            )

        return len(errors) == 0, errors

    @classmethod
    def validate_barcode_check_digit(cls, barcode: str) -> tuple[bool, list[str]]:
        """Validate the general Mod11 check digit of the barcode.

        The check digit is at position 4 of the 44-digit barcode.
        It is calculated using positions 0-3 + 5-43 (i.e., excluding
        position 4 itself).

        Args:
            barcode: The 44-digit barcode string.

        Returns:
            A tuple of (is_valid, errors).
        """
        errors = []

        check_digit = int(barcode[4])
        # Build the number without the check digit position
        number = barcode[0:4] + barcode[5:]
        calculated = cls.mod11(number)

        if check_digit != calculated:
            errors.append(
                f"Codigo de barras: digito verificador invalido "
                f"(esperado {calculated}, encontrado {check_digit})"
            )

        return len(errors) == 0, errors

    @classmethod
    def validate_full(cls, barcode: str, linha: str) -> tuple[bool, list[str]]:
        """Perform full validation on both barcode and linha digitavel.

        Args:
            barcode: The 44-digit barcode string.
            linha: The 47-digit linha digitavel string.

        Returns:
            A tuple of (is_valid, all_errors).
        """
        all_errors = []

        barcode_valid, barcode_errors = cls.validate_barcode_check_digit(barcode)
        all_errors.extend(barcode_errors)

        linha_valid, linha_errors = cls.validate_linha_digitavel_fields(linha)
        all_errors.extend(linha_errors)

        return len(all_errors) == 0, all_errors
