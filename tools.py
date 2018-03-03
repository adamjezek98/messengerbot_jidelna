from datetime import datetime


def get_class_str(c):
    classes = {
        "1.": "prima",
        "2.": "sekunda",
        "3.": "tercie",
        "4.": "kvarta",
        "5.": "kvinta",
        "6.": "sexta",
        "7.": "septima",
        "8.": "oktáva"
    }
    if str(c) in classes.keys():
        return classes[c]

    return c


def get_class_from_str(c):
    classes = {
        "prima": "1.",
        "sekunda": "2.",
        "tercie": "3.",
        "kvarta": "4.",
        "kvinta": "5.",
        "sexta": "6.",
        "septima": "7.",
        "oktáva": "8."
    }
    if str(c) in classes.keys():
        return classes[c]

    return c


def get_classes():
    return ("prima", "sekunda", "tercie", "kvarta", "kvinta", "sexta", "septima", "oktáva",
            "1.A", "1.B", "2.A", "2.B", "3.A", "3.B", "4.A", "4.B",)


def get_cs_weekday(date):
    w = int(datetime.strftime(date, "%w"))
    days = ["neděle", "pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota"]
    return days[w]
