"""Compatibilidad con la escena de juego anterior.

La primera versión del proyecto tenía una clase llamada EscenaJuego. Para
mantener la API actual y evitar romper pruebas o módulos existentes, se mantiene
una clase de compatibilidad que reutiliza la nueva escena de nivel inicial.
"""

from .escena_nivel_1 import EscenaNivel1


class EscenaJuego(EscenaNivel1):
    """Alias de compatibilidad para la primera escena jugable."""
