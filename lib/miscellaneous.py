from random import choice, randint

alphabet = "abcdefghijklmnopqrstuvwxyz"


def fill(string, n):
    while len(string) < n:
        string = choice(alphabet).upper() + string

    return string


def generate_password(n=8):
    out = ""
    for i in range(n):
        char = choice(alphabet)
        
        if randint(0, 1) == 1:
            char = char.upper()

        out += char

    return out


def generate_login(school: int, form: int, littera: str, number: int) -> str:
    school = school % 10000
    form = form % 100
    littera = littera[0].lower()
    number = number % 100

    last_number = number % 10
    school_str = ''.join(list(map(lambda x: alphabet[int(x) + last_number], str(school))))
    school_str = fill(school_str, 4)

    form_str = ''.join(list(map(lambda x: alphabet[int(x)], str(form + last_number))))
    form_str = fill(form_str, 2)

    littera_str = alphabet[-alphabet.index(littera) - 1]

    number_str = ''.join(list(map(lambda x: alphabet[int(x)], str(number))))
    number_str = fill(number_str, 2)

    additional_str = ''

    for i in range(3):
        additional_char = choice(alphabet)
        if randint(0, 1) == 1:
            additional_char = additional_char.upper()

        additional_str += additional_char


    encoded_login = school_str + form_str + littera_str + number_str + additional_str

    return encoded_login


def decode_login(login: str):
    login = login[:-3]
    school = login[:4]
    form = login[4:6]
    littera = login[6:7]
    number = login[7:9]

    return None
