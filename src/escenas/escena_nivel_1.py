"""Primera escena jugable del proyecto Guardianes del Agua."""

import pygame

from Entidades import Jugador
from ..config import ALTO_VENTANA, ANCHO_VENTANA, COLOR_FONDO, COLOR_TEXTO
from ..gestor_escenas import EstadoEscena, GestorEscenas
from .escena_base import EscenaBase


class EscenaNivel1(EscenaBase):
    """Escena inicial del juego con un prototipo mínimo funcional."""

    def __init__(self, gestor_escenas: GestorEscenas) -> None:
        self._gestor_escenas = gestor_escenas
        self._jugador = Jugador(x=120, y=100)
        self._fuente = pygame.font.Font(None, 36)
        self._suelo = pygame.Rect(0, ALTO_VENTANA - 80, ANCHO_VENTANA, 80)
        self._area_juego = pygame.Rect(0, 0, ANCHO_VENTANA, self._suelo.top)

    def manejar_evento(self, evento: pygame.event.Event) -> None:
        """Procesa entrada para el prototipo del nivel inicial."""
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._gestor_escenas.cambiar_escena(EstadoEscena.MENU)

    def actualizar(self, delta_time: float) -> None:
        """Actualiza el estado del nivel con soporte completo para delta_time."""
        teclas = pygame.key.get_pressed()
        self._jugador.actualizar_con_teclas(teclas, delta_time)
        self._jugador.limitar_en_rect(self._area_juego)

        if self._jugador.hitbox.bottom >= self._suelo.top:
            self._jugador.y = self._suelo.top - self._jugador.alto
            self._jugador.vy = 0.0
            self._jugador.actualizar_hitbox()

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja el fondo, el suelo y la entidad jugable."""
        pantalla.fill(COLOR_FONDO)
        pygame.draw.rect(pantalla, (15, 92, 110), self._suelo)

        self._jugador.dibujar(pantalla)

        etiqueta = self._fuente.render("Escena Nivel 1", True, COLOR_TEXTO)
        pantalla.blit(etiqueta, etiqueta.get_rect(topleft=(30, 20)))
