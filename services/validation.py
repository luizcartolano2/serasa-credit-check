import re


def only_digits(value: str) -> str:
    """
    Method to remove all non-digit characters from a string.
    :param value: a string that may contain digits and non-digit characters
    :return: a string containing only digits
    """
    return re.sub(r"\D", "", value)


def validate_cpf(cpf: str) -> bool:
    """
    Validate Brazilian CPF number.
    :param cpf: a string representing the CPF number, which may contain non-digit characters
    :return: a boolean indicating whether the CPF is valid
    """
    cpf = only_digits(cpf)

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # First check digit
    sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    check1 = (sum1 * 10 % 11) % 10

    # Second check digit
    sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    check2 = (sum2 * 10 % 11) % 10

    return check1 == int(cpf[9]) and check2 == int(cpf[10])


def validate_cnpj(cnpj: str) -> bool:
    """
    Validate Brazilian CNPJ number.
    :param cnpj: a string representing the CNPJ number, which may contain non-digit characters
    :return: a boolean indicating whether the CNPJ is valid
    """
    cnpj = only_digits(cnpj)

    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    weights_first = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    weights_second = [6] + weights_first

    # First check digit
    sum1 = sum(int(cnpj[i]) * weights_first[i] for i in range(12))
    check1 = 11 - (sum1 % 11)
    check1 = 0 if check1 >= 10 else check1

    # Second check digit
    sum2 = sum(int(cnpj[i]) * weights_second[i] for i in range(13))
    check2 = 11 - (sum2 % 11)
    check2 = 0 if check2 >= 10 else check2

    return check1 == int(cnpj[12]) and check2 == int(cnpj[13])
