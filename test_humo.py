def suma(a, b):
    return a + b


def saludo(nombre):
    return f"Hola, {nombre}!"


def test_suma_positivos():
    assert suma(2, 3) == 5


def test_suma_cero_negativos():
    assert suma(-1, 1) == 0


def test_saludo():
    assert saludo("Mundo") == "Hola, Mundo!"
    assert "Ana" in saludo("Ana")
