"""Primera escena jugable del proyecto Guardianes del Agua."""

import pygame

from Entidades import EnemigoVolcan, Jugador, Pez, PlantaAcuatica, ResiduoFlotante
from ..config import ALTO_VENTANA, ANCHO_VENTANA, COLOR_FONDO, COLOR_TEXTO
from ..gestor_escenas import EstadoEscena, GestorEscenas
from .escena_base import EscenaBase


class EscenaNivel1(EscenaBase):
    """Nivel inicial con una actividad breve de limpieza del agua."""

    CALIDAD_INICIAL = 25
    CALIDAD_MAXIMA = 100
    LIMITE_SUPERIOR_LAGUNA = 148
    COLOR_AGUA_CONTAMINADA = (89, 107, 78)
    COLOR_AGUA_LIMPIA = (29, 164, 203)
    COLOR_SUELO_CONTAMINADO = EnemigoVolcan.COLOR_CUERPO
    COLOR_SUELO_MUSGO = (104, 139, 71)

    def __init__(self, gestor_escenas: GestorEscenas) -> None:
        self._gestor_escenas = gestor_escenas
        self.reiniciar()

    def reiniciar(self) -> None:
        """Recrea el estado inicial del nivel para comenzar una partida nueva."""
        self._jugador = Jugador(x=120, y=165)
        self._fuente = pygame.font.Font(None, 32)
        self._fuente_ui = pygame.font.Font(None, 25)
        self._fuente_mensaje = pygame.font.Font(None, 28)
        self._suelo = pygame.Rect(0, ALTO_VENTANA - 80, ANCHO_VENTANA, 80)
        self._area_juego = pygame.Rect(
            0,
            self.LIMITE_SUPERIOR_LAGUNA,
            ANCHO_VENTANA,
            self._suelo.top - self.LIMITE_SUPERIOR_LAGUNA,
        )
        self._residuos = [
            ResiduoFlotante(pygame.Rect(350, 205, 22, 38), "Botella"),
            ResiduoFlotante(pygame.Rect(820, 240, 36, 28), "Lata", 0.6),
            ResiduoFlotante(pygame.Rect(1080, 350, 38, 30), "Bolsa", 1.2),
            ResiduoFlotante(pygame.Rect(840, 500, 24, 40), "Botella", 1.8),
            ResiduoFlotante(pygame.Rect(360, 560, 38, 28), "Lata", 2.4),
            ResiduoFlotante(pygame.Rect(150, 300, 38, 30), "Bolsa", 3.0),
            ResiduoFlotante(pygame.Rect(520, 390, 22, 38), "Botella", 3.6),
            ResiduoFlotante(pygame.Rect(1020, 215, 38, 30), "Bolsa", 4.2),
            ResiduoFlotante(pygame.Rect(670, 550, 36, 28), "Lata", 4.8),
            ResiduoFlotante(pygame.Rect(100, 500, 22, 38), "Botella", 5.4),
        ]
        self._total_residuos = len(self._residuos)
        limite_pez_izquierdo = 13
        limite_pez_derecho = ANCHO_VENTANA - 13 - Pez.ANCHO
        self._peces = [
            Pez(610, 205, 72.0, limite_pez_izquierdo, limite_pez_derecho, (55, 207, 183)),
            Pez(155, 390, -88.0, limite_pez_izquierdo, limite_pez_derecho, (255, 139, 90)),
            Pez(650, 435, 104.0, limite_pez_izquierdo, limite_pez_derecho, (113, 168, 255)),
            Pez(980, 510, -76.0, limite_pez_izquierdo, limite_pez_derecho, (226, 115, 190)),
        ]
        self._flora: list[tuple[int, PlantaAcuatica]] = [
            (35, PlantaAcuatica(95, self._suelo.top, 42, 18, (37, 91, 67))),
            (40, PlantaAcuatica(270, self._suelo.top, 74, 24, (42, 105, 72))),
            (55, PlantaAcuatica(445, self._suelo.top, 118, 30, (35, 91, 63))),
            (65, PlantaAcuatica(615, self._suelo.top, 58, 22, (48, 113, 74))),
            (75, PlantaAcuatica(790, self._suelo.top, 132, 32, (37, 98, 68))),
            (85, PlantaAcuatica(970, self._suelo.top, 88, 27, (44, 108, 72))),
            (95, PlantaAcuatica(1155, self._suelo.top, 49, 20, (39, 93, 65))),
        ]
        limite_volcan_izquierdo = 8
        limite_volcan_derecho = ANCHO_VENTANA - limite_volcan_izquierdo - EnemigoVolcan.ANCHO
        self._volcanes = [
            EnemigoVolcan(
                150,
                575,
                64.0,
                limite_volcan_izquierdo,
                limite_volcan_derecho,
                self.LIMITE_SUPERIOR_LAGUNA,
            ),
            EnemigoVolcan(
                600,
                575,
                -82.0,
                limite_volcan_izquierdo,
                limite_volcan_derecho,
                self.LIMITE_SUPERIOR_LAGUNA,
            ),
            EnemigoVolcan(
                1050,
                575,
                96.0,
                limite_volcan_izquierdo,
                limite_volcan_derecho,
                self.LIMITE_SUPERIOR_LAGUNA,
            ),
        ]
        self._calidad_agua = self.CALIDAD_INICIAL
        self._actualizar_colores_peces()
        self._mensaje = ""
        self._tiempo_mensaje = 0.0
        self._partida_terminada = False

    @property
    def calidad_agua(self) -> int:
        """Porcentaje actual de calidad del agua."""
        return self._calidad_agua

    def manejar_evento(self, evento: pygame.event.Event) -> None:
        """Procesa entrada para el prototipo del nivel inicial."""
        if self._partida_terminada:
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                self.reiniciar()
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self._gestor_escenas.cambiar_escena(EstadoEscena.MENU)
            return

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._gestor_escenas.cambiar_escena(EstadoEscena.MENU)

    def actualizar(self, delta_time: float) -> None:
        """Actualiza el estado del nivel con soporte completo para delta_time."""
        if self._partida_terminada:
            return

        teclas = pygame.key.get_pressed()
        self._jugador.actualizar_con_teclas(teclas, delta_time)
        self._jugador.limitar_en_rect(self._area_juego)

        if self._jugador.hitbox.bottom >= self._suelo.top:
            self._jugador.y = self._suelo.top - self._jugador.alto
            self._jugador.vy = 0.0
            self._jugador.actualizar_hitbox()

        for pez in self._peces:
            pez.actualizar(delta_time)
        for volcan in self._volcanes:
            volcan.actualizar(delta_time)
        for residuo in self._residuos:
            residuo.actualizar(delta_time)

        self._actualizar_interacciones(delta_time)
        if not self._partida_terminada:
            self._actualizar_ataques_volcanes()

    def _actualizar_ataques_volcanes(self) -> None:
        for volcan in self._volcanes:
            if self._jugador.hurtbox.colliderect(volcan.hurtbox):
                self._intentar_daniar_jugador(
                    volcan.DANIO_CONTACTO,
                    "Chocaste con un volcán.",
                )

            for burbuja in volcan.burbujas[:]:
                if burbuja.hurtbox.colliderect(self._jugador.hurtbox):
                    volcan.quitar_burbuja(burbuja)
                    self._intentar_daniar_jugador(
                        burbuja.danio,
                        "Una burbuja del volcán te golpeó.",
                    )

    def _intentar_daniar_jugador(self, danio: int, causa: str) -> bool:
        if (
            self._jugador.temporizador_invulnerable > 0
            or not self._jugador.salud.esta_vivo()
        ):
            return False

        self._jugador.salud.recibir_danio(danio)
        self._jugador.temporizador_invulnerable = 1.0
        if self._jugador.salud.esta_vivo():
            self._mostrar_mensaje(
                f"{causa} Salud: {self._jugador.salud.vida_actual}."
            )
        else:
            self._partida_terminada = True
            self._mensaje = "¡Fin de la partida!"
            self._tiempo_mensaje = 0.0
        return True

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja el agua, los objetos interactivos, el jugador y la guía visual."""
        pantalla.fill(COLOR_FONDO)
        pygame.draw.rect(pantalla, self._color_agua(), self._area_juego)
        pygame.draw.rect(pantalla, self._color_suelo(), self._suelo)

        for calidad_minima, planta in self._flora:
            if self._calidad_agua >= calidad_minima:
                planta.dibujar(pantalla)

        for volcan in self._volcanes:
            volcan.dibujar(pantalla)

        for residuo in self._residuos:
            self._dibujar_residuo(
                pantalla,
                residuo.rectangulo,
                residuo.tipo,
            )

        for pez in self._peces:
            pez.dibujar(pantalla)
        self._jugador.dibujar(pantalla)
        self._dibujar_hud(pantalla)
        self._dibujar_mensaje(pantalla)
        if self._partida_terminada:
            self._dibujar_fin_partida(pantalla)

    def _actualizar_interacciones(self, delta_time: float) -> None:
        if self._tiempo_mensaje > 0:
            self._tiempo_mensaje = max(0.0, self._tiempo_mensaje - delta_time)

        for pez in self._peces:
            if self._jugador.hurtbox.colliderect(pez.hurtbox):
                self._intentar_daniar_jugador(pez.DANIO, "Un pez te golpeó.")

        for residuo in self._residuos[:]:
            if self._jugador.hitbox.colliderect(residuo.rectangulo):
                self._residuos.remove(residuo)
                calidad_anterior = self._calidad_agua
                residuos_recogidos = self._total_residuos - len(self._residuos)
                self._calidad_agua = self.CALIDAD_INICIAL + (
                    (self.CALIDAD_MAXIMA - self.CALIDAD_INICIAL)
                    * residuos_recogidos
                    // self._total_residuos
                )
                mejora = self._calidad_agua - calidad_anterior
                self._actualizar_colores_peces()
                self._mostrar_mensaje(
                    f"¡Bien! {residuo.tipo} recogida. "
                    f"La calidad del agua mejora +{mejora}%."
                )

    def _actualizar_colores_peces(self) -> None:
        for pez in self._peces:
            pez.actualizar_color(self._calidad_agua)

    def _mostrar_mensaje(self, texto: str) -> None:
        self._mensaje = texto
        self._tiempo_mensaje = 4.0

    def _color_agua(self) -> tuple[int, int, int]:
        return self._interpolar_color(
            self.COLOR_AGUA_CONTAMINADA,
            self.COLOR_AGUA_LIMPIA,
            self._progreso_recuperacion(),
        )

    def _color_suelo(self) -> tuple[int, int, int]:
        return self._interpolar_color(
            self.COLOR_SUELO_CONTAMINADO,
            self.COLOR_SUELO_MUSGO,
            self._progreso_recuperacion(),
        )

    def _progreso_recuperacion(self) -> float:
        rango_calidad = self.CALIDAD_MAXIMA - self.CALIDAD_INICIAL
        return (self._calidad_agua - self.CALIDAD_INICIAL) / rango_calidad

    @staticmethod
    def _interpolar_color(
        color_inicial: tuple[int, int, int],
        color_final: tuple[int, int, int],
        progreso: float,
    ) -> tuple[int, int, int]:
        rojo = round(
            color_inicial[0]
            + (color_final[0] - color_inicial[0]) * progreso
        )
        verde = round(
            color_inicial[1]
            + (color_final[1] - color_inicial[1]) * progreso
        )
        azul = round(
            color_inicial[2]
            + (color_final[2] - color_inicial[2]) * progreso
        )
        return rojo, verde, azul

    @staticmethod
    def _dibujar_residuo(
        pantalla: pygame.Surface,
        rectangulo: pygame.Rect,
        tipo: str,
    ) -> None:
        colores = {
            "Botella": (47, 91, 77),
            "Lata": (91, 84, 57),
            "Bolsa": (79, 63, 76),
        }
        resaltados = {
            "Botella": (104, 139, 112),
            "Lata": (139, 127, 82),
            "Bolsa": (119, 96, 111),
        }
        color = colores[tipo]
        resaltado = resaltados[tipo]
        if tipo == "Botella":
            botella = [
                (rectangulo.left + 6, rectangulo.top),
                (rectangulo.right - 6, rectangulo.top),
                (rectangulo.right - 6, rectangulo.top + 8),
                (rectangulo.right - 2, rectangulo.top + 13),
                (rectangulo.right - 2, rectangulo.bottom - 3),
                (rectangulo.left + 2, rectangulo.bottom - 3),
                (rectangulo.left + 2, rectangulo.top + 13),
                (rectangulo.left + 6, rectangulo.top + 8),
            ]
            pygame.draw.polygon(pantalla, color, botella)
            pygame.draw.rect(
                pantalla,
                resaltado,
                (rectangulo.left + 8, rectangulo.top + 2, 6, 4),
                border_radius=2,
            )
            pygame.draw.line(
                pantalla,
                resaltado,
                (rectangulo.left + 6, rectangulo.top + 18),
                (rectangulo.left + 6, rectangulo.bottom - 7),
                2,
            )
        elif tipo == "Lata":
            pygame.draw.rect(
                pantalla,
                color,
                (rectangulo.left, rectangulo.top + 4, rectangulo.width, rectangulo.height - 8),
            )
            pygame.draw.ellipse(
                pantalla,
                resaltado,
                (rectangulo.left, rectangulo.top, rectangulo.width, 9),
            )
            pygame.draw.ellipse(
                pantalla,
                color,
                (rectangulo.left, rectangulo.bottom - 9, rectangulo.width, 9),
            )
            pygame.draw.line(
                pantalla,
                resaltado,
                (rectangulo.left + 5, rectangulo.top + 8),
                (rectangulo.left + 5, rectangulo.bottom - 8),
                2,
            )
        else:
            bolsa = [
                (rectangulo.left + 9, rectangulo.top + 7),
                (rectangulo.left + 13, rectangulo.top + 2),
                (rectangulo.left + 17, rectangulo.top + 7),
                (rectangulo.right - 4, rectangulo.top + 4),
                (rectangulo.right - 1, rectangulo.bottom - 3),
                (rectangulo.left + 3, rectangulo.bottom - 3),
                (rectangulo.left + 1, rectangulo.top + 5),
            ]
            pygame.draw.polygon(pantalla, color, bolsa)
            pygame.draw.line(
                pantalla,
                resaltado,
                (rectangulo.left + 7, rectangulo.top + 11),
                (rectangulo.left + 11, rectangulo.bottom - 7),
                2,
            )
            pygame.draw.line(
                pantalla,
                resaltado,
                (rectangulo.right - 8, rectangulo.top + 9),
                (rectangulo.right - 5, rectangulo.bottom - 8),
                2,
            )

    def _dibujar_hud(self, pantalla: pygame.Surface) -> None:
        panel = pygame.Rect(14, 12, 1000, 118)
        pygame.draw.rect(pantalla, (5, 33, 48), panel, border_radius=12)

        titulo = self._fuente.render("Misión: recuperar la laguna", True, COLOR_TEXTO)
        pantalla.blit(titulo, (28, 19))

        if self._calidad_agua < 40:
            estado_agua = "Muy contaminada"
        elif self._calidad_agua < 80:
            estado_agua = "En recuperación"
        else:
            estado_agua = "Saludable"

        estado = self._fuente_ui.render(
            f"Calidad del agua: {self._calidad_agua}% - {estado_agua}",
            True,
            COLOR_TEXTO,
        )
        pantalla.blit(estado, (28, 55))

        barra = pygame.Rect(365, 60, 220, 18)
        pygame.draw.rect(pantalla, (38, 55, 63), barra, border_radius=8)
        ancho_progreso = round(barra.width * self._calidad_agua / 100)
        if ancho_progreso:
            relleno = pygame.Rect(barra.x, barra.y, ancho_progreso, barra.height)
            pygame.draw.rect(pantalla, self._color_agua(), relleno, border_radius=8)
        pygame.draw.rect(pantalla, (203, 229, 232), barra, width=2, border_radius=8)

        recogidos = self._total_residuos - len(self._residuos)
        contador = self._fuente_ui.render(
            f"Residuos: {recogidos}/{self._total_residuos}",
            True,
            COLOR_TEXTO,
        )
        pantalla.blit(contador, (610, 55))
        salud = self._fuente_ui.render(
            f"Salud: {self._jugador.salud.vida_actual}",
            True,
            COLOR_TEXTO,
        )
        pantalla.blit(salud, (810, 55))

        indicacion = self._fuente_ui.render(
            "Recoge residuos y esquiva peces, volcanes y burbujas.",
            True,
            COLOR_TEXTO,
        )
        pantalla.blit(indicacion, (28, 91))

    def _dibujar_mensaje(self, pantalla: pygame.Surface) -> None:
        if self._tiempo_mensaje <= 0:
            return

        texto = self._fuente_mensaje.render(self._mensaje, True, COLOR_TEXTO)
        panel = texto.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA - 130))
        panel.inflate_ip(36, 24)
        pygame.draw.rect(pantalla, (5, 33, 48), panel, border_radius=10)
        pantalla.blit(texto, texto.get_rect(center=panel.center))

    def _dibujar_fin_partida(self, pantalla: pygame.Surface) -> None:
        capa = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        capa.fill((4, 22, 32, 205))
        pantalla.blit(capa, (0, 0))

        titulo = self._fuente.render("¡Fin de la partida!", True, COLOR_TEXTO)
        instrucciones = self._fuente_ui.render(
            "Enter: intentar de nuevo    Escape: volver al menú",
            True,
            COLOR_TEXTO,
        )
        pantalla.blit(
            titulo,
            titulo.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 - 22)),
        )
        pantalla.blit(
            instrucciones,
            instrucciones.get_rect(
                center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 + 28)
            ),
        )
