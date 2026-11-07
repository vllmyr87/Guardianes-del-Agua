"""Estado inicial provisional para enlazar el menú con el juego."""

import pygame

from ..config import (
    ALTO_VENTANA,
    ANCHO_VENTANA,
    COLOR_FONDO,
    COLOR_TEXTO,
    COLOR_TEXTO_SECUNDARIO,
)
from ..gestor_escenas import EstadoEscena, GestorEscenas
from .escena_base import EscenaBase


class EscenaJuego(EscenaBase):
    """Escena provisional hasta implementar las mecánicas del juego."""

    def __init__(self, gestor_escenas: GestorEscenas) -> None:
        self._gestor_escenas = gestor_escenas
        self._fuente_titulo = pygame.font.Font(None, 54)
        self._fuente_instrucciones = pygame.font.Font(None, 30)

    def manejar_evento(self, evento: pygame.event.Event) -> None:
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._gestor_escenas.cambiar_escena(EstadoEscena.MENU)

    def actualizar(self, delta_time: float) -> None:
        # La lógica de juego se incorporará en las siguientes etapas.
        _ = delta_time

    def dibujar(self, pantalla: pygame.Surface) -> None:
        pantalla.fill(COLOR_FONDO)

        titulo = self._fuente_titulo.render("La aventura comienza pronto", True, COLOR_TEXTO)
        instrucciones = self._fuente_instrucciones.render(
            "Presiona Esc para volver al menú",
            True,
            COLOR_TEXTO_SECUNDARIO,
        )
        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 - 24)))
        pantalla.blit(
            instrucciones,
            instrucciones.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 + 28)),
        )
