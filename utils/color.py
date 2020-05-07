def is_dark(col: str):
    """
    Проверка, темный ли переданный цвет

    :param col: Цвет в формате #rrggbb
    :return: bool
    """
    rgb = int(col[1:], 16)
    r = (rgb >> 16) & 0xff
    g = (rgb >> 8) & 0xff
    b = (rgb >> 0) & 0xff
    hsp = (0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b)) ** 0.5
    return hsp <= 127.5
