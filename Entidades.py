"""Base del modelo de entidades del juego.

Este módulo centraliza la lógica común para cualquier entidad del mundo virtual:
- posición en coordenadas X/Y,
- velocidad en los ejes X/Y,
- hitbox rectangular,
- actualización basada en delta time.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
import math
import random

import pygame


class ComponenteSalud:
    """Gestiona los puntos de vida de un personaje."""

    def __init__(self, cantidad_vida: int) -> None:
        if cantidad_vida <= 0:
            raise ValueError("La cantidad de vida inicial debe ser mayor que cero.")

        self.vida_actual = cantidad_vida

    def recibir_danio(self, cantidad: int) -> None:
        """Resta daño sin permitir que la vida actual sea negativa."""
        if cantidad < 0:
            raise ValueError("El daño no puede ser negativo.")

        self.vida_actual = max(0, self.vida_actual - cantidad)

    def esta_vivo(self) -> bool:
        """Indica si el personaje conserva puntos de vida."""
        return self.vida_actual > 0


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
        self.hurtbox = self.hitbox.copy()

    def actualizar_hitbox(self) -> None:
        """Sincroniza el rectángulo del hitbox con la posición actual."""
        self.hitbox.x = int(self.x)
        self.hitbox.y = int(self.y)
        self.hitbox.width = self.ancho
        self.hitbox.height = self.alto
        self.hurtbox.update(self.hitbox)

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
    """Dron submarino recuperador controlado por el jugador."""

    velocidad_submarina = 120.0
    COLOR_ARMADURA = (36, 87, 112)
    COLOR_BORDE = (126, 222, 231)
    COLOR_VISOR = (16, 43, 61)
    COLOR_DETALLE = (255, 190, 82)
    ANCHO = 72
    ALTO = 68

    def __init__(self, x: float, y: float, vida_inicial: int = 100) -> None:
        super().__init__(x=x, y=y, ancho=self.ANCHO, alto=self.ALTO, vx=0.0, vy=0.0)
        self.color = (76, 201, 240)
        self.salud = ComponenteSalud(vida_inicial)
        self.temporizador_invulnerable = 0.0

    def actualizar(self, delta_time: float) -> None:
        """Actualiza la lógica propia del personaje usando delta_time."""
        self.mover(delta_time)
        self.vx *= 0.82 if abs(self.vx) > 1 else 0.0
        self.vy *= 0.82 if abs(self.vy) > 1 else 0.0
        self.temporizador_invulnerable = max(
            0.0,
            self.temporizador_invulnerable - delta_time,
        )

    def actualizar_con_teclas(
        self,
        teclas: Mapping[int, bool] | Sequence[bool],
        delta_time: float,
    ) -> None:
        """Calcula velocidad horizontal y vertical a partir del teclado.

        La velocidad del personaje bajo el agua es intencionalmente menor que en
        un juego terrestre para reforzar la sensación de resistencia del medio.
        """
        vx = 0.0
        vy = 0.0

        if isinstance(teclas, Mapping):
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

        magnitud = math.hypot(vx, vy)
        if magnitud > 0:
            vx = vx / magnitud * self.velocidad_submarina
            vy = vy / magnitud * self.velocidad_submarina

        self.vx = vx
        self.vy = vy
        self.actualizar(delta_time)

    def dibujar(self, pantalla: pygame.Surface) -> None:
        x, y = self.hitbox.topleft

        for centro_x in (x + 10, x + self.ancho - 10):
            pygame.draw.circle(
                pantalla,
                self.COLOR_ARMADURA,
                (centro_x, y + 51),
                10,
            )
            pygame.draw.circle(
                pantalla,
                self.COLOR_BORDE,
                (centro_x, y + 51),
                5,
                width=2,
            )
            pygame.draw.line(
                pantalla,
                self.COLOR_DETALLE,
                (centro_x - 7, y + 51),
                (centro_x + 7, y + 51),
                2,
            )

        ala_izquierda = pygame.Rect(x + 2, y + 25, 18, 19)
        ala_derecha = pygame.Rect(x + self.ancho - 20, y + 25, 18, 19)
        for ala in (ala_izquierda, ala_derecha):
            pygame.draw.rect(
                pantalla,
                self.COLOR_ARMADURA,
                ala,
                border_radius=7,
            )
            pygame.draw.rect(
                pantalla,
                self.COLOR_BORDE,
                ala,
                width=2,
                border_radius=7,
            )

        cuerpo = pygame.Rect(x + 15, y + 14, self.ancho - 30, 43)
        pygame.draw.rect(
            pantalla,
            self.COLOR_ARMADURA,
            cuerpo,
            border_radius=14,
        )
        pygame.draw.rect(
            pantalla,
            self.COLOR_BORDE,
            cuerpo,
            width=3,
            border_radius=14,
        )

        cabina = pygame.Rect(x + 22, y + 4, self.ancho - 44, 24)
        pygame.draw.ellipse(pantalla, self.COLOR_ARMADURA, cabina)
        pygame.draw.ellipse(pantalla, self.COLOR_BORDE, cabina, width=2)
        visor = pygame.Rect(x + 26, y + 10, self.ancho - 52, 11)
        pygame.draw.ellipse(pantalla, self.COLOR_VISOR, visor)
        pygame.draw.circle(
            pantalla,
            self.COLOR_BORDE,
            (x + 32, y + 15),
            2,
        )
        pygame.draw.circle(
            pantalla,
            self.COLOR_DETALLE,
            (x + self.ancho - 32, y + 15),
            2,
        )

        pygame.draw.rect(
            pantalla,
            self.COLOR_DETALLE,
            (x + self.ancho // 2 - 5, y + 34, 10, 10),
            border_radius=5,
        )
        pygame.draw.circle(
            pantalla,
            self.COLOR_DETALLE,
            (x + self.ancho // 2, y + 3),
            3,
        )


class Pez(EntidadBase):
    """Fauna móvil que recorre la laguna y puede dañar al jugador."""

    DANIO = 8
    COLOR_INICIAL = (91, 112, 68)
    ANCHO = 58
    ALTO = 34

    def __init__(
        self,
        x: float,
        y: float,
        velocidad_x: float,
        limite_izquierdo: int,
        limite_derecho: int,
        color_final: tuple[int, int, int],
    ) -> None:
        super().__init__(
            x=x,
            y=y,
            ancho=self.ANCHO,
            alto=self.ALTO,
            vx=velocidad_x,
        )
        self._limite_izquierdo = limite_izquierdo
        self._limite_derecho = limite_derecho
        self._color_final = color_final
        self.color = self.COLOR_INICIAL

    def actualizar_color(self, calidad_agua: int) -> None:
        """Da vida al color del pez según el progreso de limpieza del lago."""
        progreso = max(0.0, min(1.0, (calidad_agua - 25) / 75))
        self.color = (
            self._interpolar_canal(0, progreso),
            self._interpolar_canal(1, progreso),
            self._interpolar_canal(2, progreso),
        )

    def _interpolar_canal(self, indice: int, progreso: float) -> int:
        inicial = self.COLOR_INICIAL[indice]
        final = self._color_final[indice]
        return round(inicial + (final - inicial) * progreso)

    def actualizar(self, delta_time: float) -> None:
        self.x += self.vx * delta_time
        if self.x < self._limite_izquierdo:
            self.x = self._limite_izquierdo
            self.vx = abs(self.vx)
        elif self.x > self._limite_derecho:
            self.x = self._limite_derecho
            self.vx = -abs(self.vx)
        self.actualizar_hitbox()

    def dibujar(self, pantalla: pygame.Surface) -> None:
        cola = [
            (self.hurtbox.left + 2, self.hurtbox.centery),
            (self.hurtbox.left - 13, self.hurtbox.top + 2),
            (self.hurtbox.left - 13, self.hurtbox.bottom - 2),
        ]
        pygame.draw.polygon(pantalla, self.color, cola)
        pygame.draw.ellipse(pantalla, self.color, self.hurtbox)
        pygame.draw.ellipse(
            pantalla,
            tuple(max(0, canal - 28) for canal in self.color),
            self.hurtbox.inflate(-18, -12),
        )
        pygame.draw.circle(
            pantalla,
            (23, 40, 48),
            (self.hurtbox.right - 13, self.hurtbox.centery - 4),
            3,
        )


class PlantaAcuatica:
    """Planta decorativa que crece desde el fondo del lago."""

    def __init__(
        self,
        x: int,
        base_y: int,
        altura: int,
        ancho_hoja: int,
        color: tuple[int, int, int],
    ) -> None:
        self.x = x
        self.base_y = base_y
        self.altura = altura
        self.ancho_hoja = ancho_hoja
        self.color = color

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja tallos y hojas de distinto tamaño sobre el lecho."""
        cantidad_tallos = max(2, self.ancho_hoja // 8)
        for indice in range(cantidad_tallos):
            desplazamiento = (indice - (cantidad_tallos - 1) / 2) * 5
            punta_x = self.x + round(desplazamiento * 1.5)
            punta_y = self.base_y - self.altura + indice * 5
            pygame.draw.line(
                pantalla,
                self.color,
                (self.x + round(desplazamiento), self.base_y),
                (punta_x, punta_y),
                3,
            )

            cantidad_hojas = max(2, self.altura // 24)
            for hoja in range(cantidad_hojas):
                progreso = (hoja + 1) / (cantidad_hojas + 1)
                centro_y = round(self.base_y - self.altura * progreso)
                direccion = -1 if (hoja + indice) % 2 else 1
                centro_x = self.x + round(desplazamiento * (1 - progreso))
                largo = max(7, self.ancho_hoja // 2)
                hoja_color = tuple(
                    min(255, canal + min(28, hoja * 3))
                    for canal in self.color
                )
                pygame.draw.ellipse(
                    pantalla,
                    hoja_color,
                    (
                        centro_x if direccion > 0 else centro_x - largo,
                        centro_y - 4,
                        largo,
                        8,
                    ),
                )


class ResiduoFlotante:
    """Residuo que oscila suavemente por el movimiento de la corriente."""

    AMPLITUD_HORIZONTAL = 3
    AMPLITUD_VERTICAL = 2
    FRECUENCIA_CORRIENTE = 1.2

    def __init__(
        self,
        rectangulo: pygame.Rect,
        tipo: str,
        fase: float = 0.0,
    ) -> None:
        self.rectangulo = rectangulo.copy()
        self.tipo = tipo
        self._x_inicial = float(rectangulo.x)
        self._y_inicial = float(rectangulo.y)
        self._fase = fase
        self._tiempo = 0.0

    def actualizar(self, delta_time: float) -> None:
        """Actualiza el vaivén sin acumular errores de redondeo."""
        self._tiempo += delta_time
        oscilacion = math.sin(
            self._fase + self._tiempo * self.FRECUENCIA_CORRIENTE
        ) - math.sin(self._fase)
        self.rectangulo.x = round(
            self._x_inicial + self.AMPLITUD_HORIZONTAL * oscilacion
        )
        self.rectangulo.y = round(
            self._y_inicial + self.AMPLITUD_VERTICAL * oscilacion
        )


class Burbuja:
    """Proyectil que asciende en línea recta desde la boca de un volcán."""

    COLOR_RELLENO = (105, 111, 108)
    COLOR_BORDE = (60, 67, 65)
    COLOR_REFLEJO = (174, 178, 169)

    def __init__(
        self,
        x: float,
        y: float,
        velocidad: float,
        radio: int,
        danio: int,
    ) -> None:
        self.x = float(x)
        self.y = float(y)
        self.velocidad = float(velocidad)
        self.radio = radio
        self.danio = danio
        self.hurtbox = pygame.Rect(0, 0, radio * 2, radio * 2)
        self._actualizar_hurtbox()

    def actualizar(self, delta_time: float) -> None:
        self.y -= self.velocidad * delta_time
        self._actualizar_hurtbox()

    def dibujar(self, pantalla: pygame.Surface) -> None:
        pygame.draw.circle(
            pantalla,
            self.COLOR_RELLENO,
            self.hurtbox.center,
            self.radio,
        )
        pygame.draw.circle(
            pantalla,
            self.COLOR_BORDE,
            self.hurtbox.center,
            self.radio,
            width=2,
        )
        pygame.draw.circle(
            pantalla,
            self.COLOR_REFLEJO,
            (self.hurtbox.centerx - self.radio // 3, self.hurtbox.centery - self.radio // 3),
            max(1, self.radio // 4),
        )

    def _actualizar_hurtbox(self) -> None:
        self.hurtbox.center = (round(self.x), round(self.y))


class EnemigoVolcan(EntidadBase):
    """Volcán móvil del fondo que genera burbujas dañinas aleatoriamente."""

    ANCHO = 72
    ALTO = 58
    DANIO_CONTACTO = 15
    DANIO_BURBUJA = 10
    VELOCIDAD_BURBUJA_MIN = 125.0
    VELOCIDAD_BURBUJA_MAX = 185.0
    INTERVALO_BURBUJA_MIN = 0.7
    INTERVALO_BURBUJA_MAX = 1.8
    PROBABILIDAD_BURBUJA_GRANDE = 0.25
    RADIO_BURBUJA_PEQUENA = (7, 11)
    RADIO_BURBUJA_GRANDE = (14, 21)
    COLOR_CUERPO = (76, 72, 48)
    COLOR_BORDE = (42, 48, 34)

    def __init__(
        self,
        x: float,
        y: float,
        velocidad_x: float,
        limite_izquierdo: int,
        limite_derecho: int,
        superficie_y: int,
    ) -> None:
        super().__init__(x=x, y=y, ancho=self.ANCHO, alto=self.ALTO, vx=velocidad_x)
        self._limite_izquierdo = limite_izquierdo
        self._limite_derecho = limite_derecho
        self._superficie_y = superficie_y
        self.burbujas: list[Burbuja] = []
        self._tiempo_hasta_burbuja = random.uniform(
            self.INTERVALO_BURBUJA_MIN,
            self.INTERVALO_BURBUJA_MAX,
        )

    def actualizar(self, delta_time: float) -> None:
        self.x += self.vx * delta_time
        if self.x < self._limite_izquierdo:
            self.x = self._limite_izquierdo
            self.vx = abs(self.vx)
        elif self.x > self._limite_derecho:
            self.x = self._limite_derecho
            self.vx = -abs(self.vx)
        self.actualizar_hitbox()

        self._tiempo_hasta_burbuja -= delta_time
        if self._tiempo_hasta_burbuja <= 0:
            self._crear_burbuja()
            self._tiempo_hasta_burbuja = random.uniform(
                self.INTERVALO_BURBUJA_MIN,
                self.INTERVALO_BURBUJA_MAX,
            )

        burbujas_activas: list[Burbuja] = []
        for burbuja in self.burbujas:
            burbuja.actualizar(delta_time)
            if burbuja.hurtbox.bottom > self._superficie_y:
                burbujas_activas.append(burbuja)
        self.burbujas = burbujas_activas

    def dibujar(self, pantalla: pygame.Surface) -> None:
        cuerpo = [
            (self.hitbox.left, self.hitbox.bottom),
            (self.hitbox.left + 9, self.hitbox.top + 25),
            (self.hitbox.left + 23, self.hitbox.top + 18),
            (self.hitbox.centerx, self.hitbox.top + 4),
            (self.hitbox.right - 21, self.hitbox.top + 18),
            (self.hitbox.right - 8, self.hitbox.top + 25),
            (self.hitbox.right, self.hitbox.bottom),
        ]
        pygame.draw.polygon(pantalla, self.COLOR_CUERPO, cuerpo)
        pygame.draw.polygon(pantalla, self.COLOR_BORDE, cuerpo, width=3)
        boca = pygame.Rect(self.hitbox.centerx - 13, self.hitbox.top + 3, 26, 12)
        pygame.draw.ellipse(pantalla, (30, 34, 27), boca)

        for burbuja in self.burbujas:
            burbuja.dibujar(pantalla)

    def quitar_burbuja(self, burbuja: Burbuja) -> None:
        """Retira una burbuja después de que impacta al jugador."""
        self.burbujas.remove(burbuja)

    def _crear_burbuja(self) -> None:
        radio_minimo, radio_maximo = (
            self.RADIO_BURBUJA_GRANDE
            if random.random() < self.PROBABILIDAD_BURBUJA_GRANDE
            else self.RADIO_BURBUJA_PEQUENA
        )
        self.burbujas.append(
            Burbuja(
                x=self.hitbox.centerx,
                y=self.hitbox.top + 7,
                velocidad=random.uniform(
                    self.VELOCIDAD_BURBUJA_MIN,
                    self.VELOCIDAD_BURBUJA_MAX,
                ),
                radio=random.randint(radio_minimo, radio_maximo),
                danio=self.DANIO_BURBUJA,
            )
        )


__all__ = [
    "Burbuja",
    "ComponenteSalud",
    "EnemigoVolcan",
    "EntidadBase",
    "Jugador",
    "PlantaAcuatica",
    "Pez",
    "ResiduoFlotante",
]
