"""Tests de contrato para README.md (perfil skvkel/slvkel).

Solo lectura local, sin red ni dependencias externas.
"""
from pathlib import Path

README_PATH = Path(__file__).resolve().parent.parent / "README.md"


def _leer_readme():
    assert README_PATH.is_file(), f"no existe {README_PATH}"
    texto = README_PATH.read_text(encoding="utf-8")
    return texto


def test_readme_exists():
    """CA1: README.md existe en la raiz."""
    assert README_PATH.is_file()


def test_readme_no_vacio():
    """CA2: README no vacio."""
    texto = _leer_readme()
    assert texto.strip() != ""
    assert len(texto) > 100


def test_readme_contiene_cabecera():
    """CA2: contiene cabecera esperada."""
    texto = _leer_readme()
    assert "Hi! I'm Slvkel" in texto


def test_readme_contiene_secciones():
    """CA3: secciones clave presentes sin requerir red."""
    texto = _leer_readme()
    for seccion in ("Spotify Playing", "Languages and Tools", "Frontend and Backend", "Databases"):
        assert seccion in texto, f"falta seccion: {seccion}"
