from decimal import localcontext, Decimal, ROUND_HALF_UP

import locale


def redondear(numero):
    with localcontext() as ctx:
        ctx.rounding = ROUND_HALF_UP
        n = Decimal(numero)
        return int(n.to_integral_value())
    


def formatear_dict_numero(dictionary):
    for k, v in dictionary.items():
        dictionary[k] = locale.format_string("%d", v, grouping=True, monetary=True)
    return dictionary