import pytest
from services.validation import validate_cpf, validate_cnpj


class TestCPFValidation:
    """
    Tests for CPF validation function.
    """

    def test_valid_cpf(self):
        """
        Test a valid CPF number.
        :return: assertion that the CPF is valid
        """
        assert validate_cpf("123.456.789-09") is True

    @pytest.mark.parametrize(
        "cpf", ["123.456.789", "111.111.111-11", "abc.def.ghi-jk"]  # wrong length  # repeated digits  # invalid characters
    )
    def test_invalid_cpf(self, cpf):
        """
        Test invalid CPF numbers.
        :param cpf: a string representing the CPF number
        :return: assertion that the CPF is invalid
        """
        assert validate_cpf(cpf) is False


class TestCNPJValidation:
    """
    Tests for CNPJ validation function.
    """

    def test_valid_cnpj(self):
        """
        Test a valid CNPJ number.
        :return: assertion that the CNPJ is valid
        """
        assert validate_cnpj("12.345.678/0001-95") is True

    @pytest.mark.parametrize(
        "cnpj",
        [
            "12.345.678/0001",  # wrong length
            "11.111.111/1111-11",  # repeated digits
            "ab.cd.efg/hijk-lm",  # invalid characters
        ],
    )
    def test_invalid_cnpj(self, cnpj):
        """
        Test invalid CNPJ numbers.
        :param cnpj: a string representing the CNPJ number
        :return: assertion that the CNPJ is invalid
        """
        assert validate_cnpj(cnpj) is False
