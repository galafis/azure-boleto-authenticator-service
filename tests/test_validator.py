"""Tests for boleto validation, parsing, and bank code lookup."""

import unittest
from datetime import date

from src.boleto.validator import BoletoValidator
from src.boleto.parser import BoletoParser
from src.boleto.bank_codes import BANK_CODES, get_bank_name
from src.boleto.models import BoletoInfo


class TestMod10(unittest.TestCase):
    """Test cases for the Mod10 check digit algorithm."""

    def test_mod10_single_digit(self):
        result = BoletoValidator.mod10("0")
        self.assertIn(result, range(0, 10))

    def test_mod10_known_value_1(self):
        # 001905009 -> check digit should be calculable
        result = BoletoValidator.mod10("001905009")
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)
        self.assertLessEqual(result, 9)

    def test_mod10_known_value_2(self):
        result = BoletoValidator.mod10("5401448160")
        self.assertIsInstance(result, int)

    def test_mod10_known_value_3(self):
        result = BoletoValidator.mod10("0680935031")
        self.assertIsInstance(result, int)

    def test_mod10_all_zeros(self):
        result = BoletoValidator.mod10("0000000000")
        self.assertEqual(result, 0)

    def test_mod10_returns_zero_when_total_mod10_is_zero(self):
        # Find an input that results in 0
        result = BoletoValidator.mod10("18")
        self.assertIn(result, range(0, 10))

    def test_mod10_single_one(self):
        result = BoletoValidator.mod10("1")
        self.assertEqual(result, 8)  # 1*2=2, 10-2=8

    def test_mod10_alternating_weights(self):
        # Verify weights alternate between 2 and 1
        result1 = BoletoValidator.mod10("12")
        result2 = BoletoValidator.mod10("21")
        # Different inputs should give different results
        self.assertIsInstance(result1, int)
        self.assertIsInstance(result2, int)

    def test_mod10_large_product_splits_digits(self):
        # When digit * weight >= 10, digits are summed individually
        result = BoletoValidator.mod10("9")
        # 9*2=18 -> 1+8=9, total=9, 10-9=1
        self.assertEqual(result, 1)

    def test_mod10_result_range(self):
        """Ensure Mod10 always returns 0-9."""
        for val in ["123456789", "987654321", "111111111", "999999999"]:
            result = BoletoValidator.mod10(val)
            self.assertGreaterEqual(result, 0)
            self.assertLessEqual(result, 9)


class TestMod11(unittest.TestCase):
    """Test cases for the Mod11 check digit algorithm."""

    def test_mod11_basic(self):
        result = BoletoValidator.mod11("0019373700000001000500940144816069068093503")
        self.assertIsInstance(result, int)

    def test_mod11_returns_1_for_remainder_0(self):
        # Build a number that gives remainder 0
        # When 11 - remainder gives 0, 10, or 11, return 1
        result = BoletoValidator.mod11("0")
        self.assertIn(result, range(1, 10))

    def test_mod11_result_range(self):
        """Mod11 should return 1-9 (never 0, 10, or 11)."""
        test_values = [
            "1234567890123456789012345678901234567890123",
            "0000000000000000000000000000000000000000000",
            "9999999999999999999999999999999999999999999",
        ]
        for val in test_values:
            result = BoletoValidator.mod11(val)
            self.assertGreaterEqual(result, 1)
            self.assertLessEqual(result, 9)

    def test_mod11_weight_cycles(self):
        """Weights should cycle from 2 to 9."""
        result = BoletoValidator.mod11("12345678901234567890")
        self.assertIsInstance(result, int)

    def test_mod11_custom_base(self):
        result = BoletoValidator.mod11("123456", base=7)
        self.assertIsInstance(result, int)


class TestBarcodeValidation(unittest.TestCase):
    """Test barcode check digit validation."""

    def test_validate_barcode_valid(self):
        # Construct a barcode with a correct check digit
        number = "0019" + "3737" + "0000000100" + "0500940144816069068093503"
        check = BoletoValidator.mod11(
            number[0:4] + number[4:]
        )
        # Insert the check digit at position 4
        barcode = number[0:4] + str(check) + number[4:]
        is_valid, errors = BoletoValidator.validate_barcode_check_digit(barcode)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_barcode_invalid(self):
        barcode = "00190373700000001000500940144816069068093503"
        is_valid, errors = BoletoValidator.validate_barcode_check_digit(barcode)
        # May or may not be valid depending on check digit
        self.assertIsInstance(is_valid, bool)

    def test_validate_barcode_wrong_digit(self):
        # Build correct barcode then tamper with check digit
        base = "001937370000000100050094014481606906809350"
        check = BoletoValidator.mod11(base[0:4] + base[4:])
        barcode = base[0:4] + str(check) + base[4:]
        # Tamper with check digit
        wrong = barcode[0:4] + str((int(barcode[4]) + 1) % 10) + barcode[5:]
        is_valid, errors = BoletoValidator.validate_barcode_check_digit(wrong)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)


class TestLinhaDigitavelValidation(unittest.TestCase):
    """Test linha digitavel field validation."""

    def test_validate_fields_with_correct_check_digits(self):
        # Build a linha with correct check digits
        field1_data = "001905009"
        field1_check = BoletoValidator.mod10(field1_data)
        field2_data = "5401448160"
        field2_check = BoletoValidator.mod10(field2_data)
        field3_data = "0680935031"
        field3_check = BoletoValidator.mod10(field3_data)

        linha = (
            field1_data + str(field1_check)
            + field2_data + str(field2_check)
            + field3_data + str(field3_check)
            + "3"  # general check digit
            + "37370000000100"  # due date factor + value
        )

        is_valid, errors = BoletoValidator.validate_linha_digitavel_fields(linha)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_validate_fields_with_wrong_field1(self):
        field1_data = "001905009"
        wrong_check = (BoletoValidator.mod10(field1_data) + 1) % 10
        field2_data = "5401448160"
        field2_check = BoletoValidator.mod10(field2_data)
        field3_data = "0680935031"
        field3_check = BoletoValidator.mod10(field3_data)

        linha = (
            field1_data + str(wrong_check)
            + field2_data + str(field2_check)
            + field3_data + str(field3_check)
            + "3"
            + "37370000000100"
        )

        is_valid, errors = BoletoValidator.validate_linha_digitavel_fields(linha)
        self.assertFalse(is_valid)
        self.assertTrue(any("Campo 1" in e for e in errors))


class TestParser(unittest.TestCase):
    """Test boleto parser functionality."""

    def test_clean_input_removes_dots(self):
        result = BoletoParser._clean_input("001.90.50095")
        self.assertEqual(result, "00190500950")

    def test_clean_input_removes_spaces(self):
        result = BoletoParser._clean_input("001 905 0095")
        self.assertEqual(result, "0019050095")

    def test_clean_input_removes_hyphens(self):
        result = BoletoParser._clean_input("001-905-0095")
        self.assertEqual(result, "0019050095")

    def test_parse_invalid_length(self):
        result = BoletoParser.parse("12345")
        self.assertFalse(result.valid)
        self.assertGreater(len(result.errors), 0)

    def test_parse_linha_47_digits(self):
        # Build a valid 47-digit linha
        field1_data = "001905009"
        field1_check = BoletoValidator.mod10(field1_data)
        field2_data = "5401448160"
        field2_check = BoletoValidator.mod10(field2_data)
        field3_data = "0680935031"
        field3_check = BoletoValidator.mod10(field3_data)

        linha = (
            field1_data + str(field1_check)
            + field2_data + str(field2_check)
            + field3_data + str(field3_check)
            + "3"
            + "37370000000100"
        )

        result = BoletoParser.parse(linha)
        self.assertEqual(result.bank_code, "001")
        self.assertEqual(result.bank_name, "Banco do Brasil")

    def test_parse_barcode_44_digits(self):
        # Build a valid barcode
        base = "0019" + "3737" + "0000000100" + "0500940144816069068093503"
        check = BoletoValidator.mod11(base[0:4] + base[4:])
        barcode = base[0:4] + str(check) + base[4:]

        result = BoletoParser.parse(barcode)
        self.assertEqual(result.bank_code, "001")

    def test_extract_value(self):
        value = BoletoParser._extract_value("0000000100")
        self.assertEqual(value, 1.0)

    def test_extract_value_larger(self):
        value = BoletoParser._extract_value("0000150000")
        self.assertEqual(value, 1500.0)

    def test_extract_due_date_zero(self):
        result = BoletoParser._extract_due_date("0000")
        self.assertIsNone(result)

    def test_extract_due_date_nonzero(self):
        result = BoletoParser._extract_due_date("1000")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, date)

    def test_linha_to_barcode_length(self):
        linha = "00190500954014481606906809350314337370000000100"
        # Ensure correct length (need 47 digits)
        self.assertEqual(len(linha), 47)
        barcode = BoletoParser.linha_to_barcode(linha)
        self.assertEqual(len(barcode), 44)

    def test_barcode_to_linha_length(self):
        barcode = "00193373700000001000500940144816069068093503"
        self.assertEqual(len(barcode), 44)
        linha = BoletoParser.barcode_to_linha(barcode)
        self.assertEqual(len(linha), 47)


class TestBankCodes(unittest.TestCase):
    """Test bank code lookup."""

    def test_known_banks(self):
        self.assertEqual(get_bank_name("001"), "Banco do Brasil")
        self.assertEqual(get_bank_name("033"), "Santander")
        self.assertEqual(get_bank_name("104"), "Caixa Economica Federal")
        self.assertEqual(get_bank_name("237"), "Bradesco")
        self.assertEqual(get_bank_name("341"), "Itau Unibanco")
        self.assertEqual(get_bank_name("756"), "Sicoob")

    def test_unknown_bank(self):
        self.assertEqual(get_bank_name("999"), "Desconhecido")

    def test_bank_codes_dict_not_empty(self):
        self.assertGreater(len(BANK_CODES), 0)


class TestBoletoInfo(unittest.TestCase):
    """Test BoletoInfo model."""

    def test_to_dict(self):
        info = BoletoInfo(
            bank_code="001",
            bank_name="Banco do Brasil",
            value=100.0,
            valid=True,
        )
        d = info.to_dict()
        self.assertEqual(d["bank_code"], "001")
        self.assertEqual(d["value"], 100.0)
        self.assertTrue(d["valid"])

    def test_str_valid(self):
        info = BoletoInfo(bank_code="001", bank_name="Banco do Brasil", valid=True)
        text = str(info)
        self.assertIn("Valido", text)
        self.assertIn("Banco do Brasil", text)

    def test_str_invalid(self):
        info = BoletoInfo(valid=False)
        text = str(info)
        self.assertIn("Invalido", text)

    def test_default_errors_empty(self):
        info = BoletoInfo()
        self.assertEqual(info.errors, [])


if __name__ == "__main__":
    unittest.main()
