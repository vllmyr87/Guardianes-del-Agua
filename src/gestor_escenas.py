"""Registro y control del estado activo del juego."""

from enum import Enum, auto

import pygame

from .escenas.escena_base import EscenaBase


class EstadoEscena(Enum):
    """Estados disponibles para las escenas principales del juego."""

    MENU = auto()
    JUEGO = auto()


class GestorEscenas:
    """Mantiene las escenas registradas y delega en la escena activa."""

    def __init__(self) -> None:
        self._escenas: dict[EstadoEscena, EscenaBase] = {}
        self._estado_actual: EstadoEscena | None = None

    def registrar_escena(self, estado: EstadoEscena, escena: EscenaBase) -> None:
        """Registra una escena para un estado, evitando reemplazos accidentales."""
        if estado in self._escenas:
            raise ValueError(f"Ya existe una escena registrada para {estado.name}.")

        self._escenas[estado] = escena

    def cambiar_escena(self, estado: EstadoEscena) -> None:
        """Activa una escena previamente registrada."""
        if estado not in self._escenas:
            raise KeyError(f"No hay ninguna escena registrada para {estado.name}.")

        self._estado_actual = estado

    @property
    def escena_actual(self) -> EscenaBase:
        """Devuelve la escena activa o informa si aún no se configuró."""
        if self._estado_actual is None:
            raise RuntimeError("No hay una escena activa. Activa una escena antes de iniciar el juego.")

        return self._escenas[self._estado_actual]

    def manejar_evento(self, evento: pygame.event.Event) -> None:
        """Envía los eventos de entrada a la escena activa."""
        self.escena_actual.manejar_evento(evento)

    def actualizar(self, delta_time: float) -> None:
        """Actualiza la escena activa; delta_time se expresa en segundos."""
        self.escena_actual.actualizar(delta_time)

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja la escena activa en la superficie de la ventana."""
        self.escena_actual.dibujar(pantalla)
