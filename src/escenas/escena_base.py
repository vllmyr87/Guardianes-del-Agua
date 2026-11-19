"""Contrato abstracto que deben implementar las escenas del juego."""

from abc import ABC, abstractmethod

import pygame


class EscenaBase(ABC):
    """Interfaz común para actualización, entrada y dibujo de escenas."""

    def manejar_evento(self, evento: pygame.event.Event) -> None:
        """Procesa un evento de Pygame; las escenas pueden sobrescribirlo."""

    def reiniciar(self) -> None:
        """Restablece la escena si esta conserva estado entre partidas."""

    @abstractmethod
    def actualizar(self, delta_time: float) -> None:
        """Actualiza la lógica de la escena usando delta_time en segundos."""

    @abstractmethod
    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja el estado actual de la escena en la pantalla."""
