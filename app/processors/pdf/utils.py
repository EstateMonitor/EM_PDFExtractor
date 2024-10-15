def string_cleanup(raw_string):
    """
    Очищает строку от лишних символов, пробелов и т.д.
    :param raw_string: Строка для очистки
    :return: Очищенная строка
    """

    # Удаление символов переноса строки
    raw_string = raw_string.replace('\n', '')

    # Удаление лишних пробелов, даже если их больше трёх подряд
    raw_string = ' '.join(raw_string.split())

    # Удаление символов табуляции
    raw_string = raw_string.replace('\t', '')

    return raw_string
