"""Base del modelo de entidades del juego.

Este módulo centraliza la lógica común para cualquier entidad del mundo virtual:
- posición en coordenadas X/Y,
- velocidad en los ejes X/Y,
- hitbox rectangular,
- actualización basada en delta time.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pygame


class EntidadBase(ABC):
    """Clase abstracta que define la estructura mínima de una entidad del juego."""

    def __init__(
        self,
        x: float,
        y: float,
        ancho: int,
        alto: int,
        vx: float = 0.0,
        vy: float = 0.0,
    ) -> None:
        self.x = float(x)
        self.y = float(y)
        self.ancho = int(ancho)
        self.alto = int(alto)
        self.vx = float(vx)
        self.vy = float(vy)
        self.hitbox = pygame.Rect(self.x, self.y, self.ancho, self.alto)

    def actualizar_hitbox(self) -> None:
        """Sincroniza el rectángulo del hitbox con la posición actual."""
        self.hitbox.x = int(self.x)
        self.hitbox.y = int(self.y)
        self.hitbox.width = self.ancho
        self.hitbox.height = self.alto

    def limitar_en_rect(self, limites: pygame.Rect) -> None:
        """Mantiene a la entidad dentro de un rectángulo definido del mundo."""
        self.x = max(limites.left, min(self.x, limites.right - self.ancho))
        self.y = max(limites.top, min(self.y, limites.bottom - self.alto))
        self.actualizar_hitbox()

    def mover(self, delta_time: float) -> None:
        """Aplica la velocidad usando tiempo real en segundos."""
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        self.actualizar_hitbox()

    def aplicar_gravedad(self, delta_time: float, gravedad: float = 980.0) -> None:
        """Integración simple de gravedad preparada para delta_time."""
        self.vy += gravedad * delta_time
        self.mover(delta_time)

    @abstractmethod
    def actualizar(self, delta_time: float) -> None:
        """Actualiza la lógica específica de cada entidad."""

    @abstractmethod
    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja la entidad sobre la pantalla indicada."""


class Jugador(EntidadBase):
    """Entidad jugable del protagonista submarino."""

    velocidad_submarina = 120.0

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x=x, y=y, ancho=32, alto=48, vx=0.0, vy=0.0)
        self.color = (76, 201, 240)

    def actualizar(self, delta_time: float) -> None:
        """Actualiza la lógica propia del personaje usando delta_time."""
        self.mover(delta_time)
        self.vx *= 0.82 if abs(self.vx) > 1 else 0.0
        self.vy *= 0.82 if abs(self.vy) > 1 else 0.0

    def actualizar_con_teclas(self, teclas: object, delta_time: float) -> None:
        """Calcula velocidad horizontal y vertical a partir del teclado.

        La velocidad del personaje bajo el agua es intencionalmente menor que en
        un juego terrestre para reforzar la sensación de resistencia del medio.
        """
        vx = 0.0
        vy = 0.0

        if hasattr(teclas, "get"):
            izquierda = bool(teclas.get(pygame.K_LEFT, False)) or bool(teclas.get(pygame.K_a, False))
            derecha = bool(teclas.get(pygame.K_RIGHT, False)) or bool(teclas.get(pygame.K_d, False))
            arriba = bool(teclas.get(pygame.K_UP, False)) or bool(teclas.get(pygame.K_w, False))
            abajo = bool(teclas.get(pygame.K_DOWN, False)) or bool(teclas.get(pygame.K_s, False))
        else:
            izquierda = bool(teclas[pygame.K_LEFT]) or bool(teclas[pygame.K_a])
            derecha = bool(teclas[pygame.K_RIGHT]) or bool(teclas[pygame.K_d])
            arriba = bool(teclas[pygame.K_UP]) or bool(teclas[pygame.K_w])
            abajo = bool(teclas[pygame.K_DOWN]) or bool(teclas[pygame.K_s])

        if izquierda:
            vx -= self.velocidad_submarina
        if derecha:
            vx += self.velocidad_submarina
        if arriba:
            vy -= self.velocidad_submarina
        if abajo:
            vy += self.velocidad_submarina

        self.vx = vx
        self.vy = vy
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        self.actualizar_hitbox()

    def dibujar(self, pantalla: pygame.Surface) -> None:
        pygame.draw.rect(pantalla, self.color, self.hitbox, border_radius=8)


__all__ = ["EntidadBase", "Jugador"]
