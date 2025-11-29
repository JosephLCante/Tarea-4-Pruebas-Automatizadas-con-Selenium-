# helpers genéricos para tests (opcional)
import random
import string

def random_email(prefix="test"):
    return f"{prefix}{''.join(random.choices(string.ascii_lowercase+string.digits, k=6))}@example.com"

def random_name():
    return "Name" + ''.join(random.choices(string.ascii_letters, k=5))
