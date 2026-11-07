"""Menú inicial y entrada a la primera escena jugable."""

import pygame

from ..config import (
    ALTO_VENTANA,
    ANCHO_VENTANA,
    COLOR_BORDE_BOTON,
    COLOR_BOTON,
    COLOR_BOTON_HOVER,
    COLOR_FONDO,
    COLOR_TEXTO,
    COLOR_TEXTO_SECUNDARIO,
)
from ..gestor_escenas import EstadoEscena, GestorEscenas
from .escena_base import EscenaBase


class EscenaMenu(EscenaBase):
    """Presenta el título y el botón para comenzar la aventura."""

    def __init__(self, gestor_escenas: GestorEscenas) -> None:
        self._gestor_escenas = gestor_escenas
        self._fuente_titulo = pygame.font.Font(None, 76)
        self._fuente_subtitulo = pygame.font.Font(None, 32)
        self._fuente_boton = pygame.font.Font(None, 38)
        self._boton_comenzar = pygame.Rect(0, 0, 260, 68)
        self._boton_comenzar.center = (ANCHO_VENTANA // 2, ALTO_VENTANA // 2 + 70)
        self._mouse_sobre_boton = False

    def manejar_evento(self, evento: pygame.event.Event) -> None:
        if evento.type == pygame.MOUSEMOTION:
            self._mouse_sobre_boton = self._boton_comenzar.collidepoint(evento.pos)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self._boton_comenzar.collidepoint(evento.pos):
                self._comenzar()
        elif evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._comenzar()

    def actualizar(self, delta_time: float) -> None:
        # La escena no tiene animaciones todavía; delta_time queda disponible para ellas.
        _ = delta_time

    def dibujar(self, pantalla: pygame.Surface) -> None:
        pantalla.fill(COLOR_FONDO)

        titulo = self._fuente_titulo.render("Guardianes del Agua", True, COLOR_TEXTO)
        subtitulo = self._fuente_subtitulo.render(
            "Una aventura para proteger cada gota",
            True,
            COLOR_TEXTO_SECUNDARIO,
        )
        etiqueta_boton = self._fuente_boton.render("Comenzar", True, COLOR_TEXTO)

        pantalla.blit(titulo, titulo.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 - 90)))
        pantalla.blit(
            subtitulo,
            subtitulo.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 - 28)),
        )

        color_boton = COLOR_BOTON_HOVER if self._mouse_sobre_boton else COLOR_BOTON
        pygame.draw.rect(pantalla, color_boton, self._boton_comenzar, border_radius=12)
        pygame.draw.rect(
            pantalla,
            COLOR_BORDE_BOTON,
            self._boton_comenzar,
            width=2,
            border_radius=12,
        )
        pantalla.blit(etiqueta_boton, etiqueta_boton.get_rect(center=self._boton_comenzar.center))

    def _comenzar(self) -> None:
        self._gestor_escenas.cambiar_escena(EstadoEscena.JUEGO)
