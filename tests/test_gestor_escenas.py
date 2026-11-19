"""Pruebas del cambio de estado y del flujo inicial del menú."""

import math
import unittest
from unittest.mock import patch

import pygame

from Entidades import (
    Burbuja,
    ComponenteSalud,
    EnemigoVolcan,
    Jugador,
    Pez,
    PlantaAcuatica,
    ResiduoFlotante,
)
from src.escenas.escena_menu import EscenaMenu
from src.escenas.escena_nivel_1 import EscenaNivel1
from src.config import ANCHO_VENTANA, COLOR_FONDO
from src.gestor_escenas import EstadoEscena, GestorEscenas


class GestorEscenasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def setUp(self) -> None:
        self.gestor = GestorEscenas()
        self.gestor.registrar_escena(EstadoEscena.MENU, EscenaMenu(self.gestor))
        self.escena_nivel = EscenaNivel1(self.gestor)
        self.gestor.registrar_escena(EstadoEscena.JUEGO, self.escena_nivel)
        self.gestor.cambiar_escena(EstadoEscena.MENU)

    def test_tecla_enter_inicia_el_juego(self) -> None:
        evento = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)

        self.gestor.manejar_evento(evento)

        self.assertIsInstance(self.gestor.escena_actual, EscenaNivel1)

    def test_clic_en_comenzar_inicia_el_juego(self) -> None:
        evento = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=(640, 430),
        )

        self.gestor.manejar_evento(evento)

        self.assertIsInstance(self.gestor.escena_actual, EscenaNivel1)

    def test_tecla_escape_vuelve_al_menu(self) -> None:
        self.gestor.cambiar_escena(EstadoEscena.JUEGO)
        evento = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)

        self.gestor.manejar_evento(evento)

        self.assertIsInstance(self.gestor.escena_actual, EscenaMenu)

    def test_escena_activa_se_actualiza_y_dibuja(self) -> None:
        pantalla = pygame.Surface((1280, 720))

        self.gestor.actualizar(1 / 60)
        self.gestor.dibujar(pantalla)

        self.assertEqual(pantalla.get_at((0, 0))[:3], COLOR_FONDO)

    def test_laguna_y_elementos_de_juego_quedan_bajo_el_panel_de_datos(self) -> None:
        escena = EscenaNivel1(self.gestor)
        pantalla = pygame.Surface((1280, 720))

        escena.dibujar(pantalla)

        self.assertEqual(
            escena._area_juego.top,
            escena.LIMITE_SUPERIOR_LAGUNA,
        )
        self.assertGreaterEqual(escena._jugador.hitbox.top, escena._area_juego.top)
        self.assertTrue(
            all(
                residuo.rectangulo.top >= escena._area_juego.top
                for residuo in escena._residuos
            )
        )
        self.assertEqual(pantalla.get_at((0, 140))[:3], COLOR_FONDO)
        self.assertEqual(pantalla.get_at((0, 148))[:3], escena._color_agua())

    def test_hay_cuatro_peces_visibles_y_dentro_de_la_laguna(self) -> None:
        escena = EscenaNivel1(self.gestor)

        self.assertEqual(len(escena._peces), 4)
        self.assertTrue(all(isinstance(pez, Pez) for pez in escena._peces))
        self.assertTrue(
            all(
                pez.hurtbox.top >= escena._area_juego.top
                and pez.hurtbox.bottom <= escena._suelo.top
                for pez in escena._peces
            )
        )

    def test_peces_se_mueven_horizontalmente_con_delta_time(self) -> None:
        escena = EscenaNivel1(self.gestor)
        posiciones_iniciales = [pez.x for pez in escena._peces]

        escena.actualizar(0.1)

        self.assertTrue(
            any(pez.x != x for pez, x in zip(escena._peces, posiciones_iniciales))
        )

    def test_peces_y_volcanes_recorran_los_bordes_sin_salir_de_pantalla(
        self,
    ) -> None:
        escena = EscenaNivel1(self.gestor)
        for pez in escena._peces:
            pez.x = pez._limite_izquierdo
            pez.vx = -100.0
            pez.actualizar(0.1)
            self.assertEqual(pez.x, pez._limite_izquierdo)
            self.assertGreaterEqual(pez.hurtbox.left - 13, 0)

            pez.x = pez._limite_derecho
            pez.vx = 100.0
            pez.actualizar(0.1)
            self.assertEqual(pez.x, pez._limite_derecho)
            self.assertLessEqual(pez.hurtbox.right, ANCHO_VENTANA)

        for volcan in escena._volcanes:
            volcan.x = volcan._limite_izquierdo
            volcan.vx = -100.0
            volcan.actualizar(0)
            self.assertEqual(volcan.x, volcan._limite_izquierdo)
            self.assertGreaterEqual(volcan.hitbox.left, 0)

            volcan.x = volcan._limite_derecho
            volcan.vx = 100.0
            volcan.actualizar(0)
            self.assertEqual(volcan.x, volcan._limite_derecho)
            self.assertLessEqual(volcan.hitbox.right, ANCHO_VENTANA)

    def test_volcanes_se_mueven_y_pueden_cruzarse(self) -> None:
        escena = EscenaNivel1(self.gestor)
        self.assertEqual(len(escena._volcanes), 3)
        posiciones = sorted(volcan.x for volcan in escena._volcanes)
        self.assertTrue(
            all(
                derecha - izquierda >= 400
                for izquierda, derecha in zip(posiciones, posiciones[1:])
            )
        )
        primero, segundo = escena._volcanes[:2]
        primero.x = 200
        segundo.x = 240
        primero.vx = 100
        segundo.vx = -100
        primero._tiempo_hasta_burbuja = 10
        segundo._tiempo_hasta_burbuja = 10
        primero.actualizar_hitbox()
        segundo.actualizar_hitbox()

        primero.actualizar(0.3)
        segundo.actualizar(0.3)

        self.assertGreater(primero.x, segundo.x)
        self.assertTrue(all(isinstance(volcan, EnemigoVolcan) for volcan in escena._volcanes))
        self.assertTrue(
            all(volcan.hitbox.bottom <= escena._suelo.top for volcan in escena._volcanes)
        )

    def test_volcanes_generan_burbujas_que_suben_y_desaparecen_en_superficie(self) -> None:
        escena = EscenaNivel1(self.gestor)
        volcan = escena._volcanes[0]
        volcan._tiempo_hasta_burbuja = 0

        volcan.actualizar(0)

        self.assertEqual(len(volcan.burbujas), 1)
        burbuja = volcan.burbujas[0]
        self.assertIsInstance(burbuja, Burbuja)
        y_inicial = burbuja.y
        x_inicial = burbuja.x
        volcan.actualizar(0.1)
        self.assertLess(burbuja.y, y_inicial)
        self.assertEqual(burbuja.x, x_inicial)

        volcan.burbujas.clear()
        volcan._tiempo_hasta_burbuja = 10
        burbuja_cerca_de_superficie = Burbuja(
            x=volcan.hitbox.centerx,
            y=escena.LIMITE_SUPERIOR_LAGUNA + 30,
            velocidad=200,
            radio=8,
            danio=10,
        )
        volcan.burbujas.append(burbuja_cerca_de_superficie)
        volcan.actualizar(0.3)

        self.assertEqual(volcan.burbujas, [])

    def test_burbujas_son_grises_y_pueden_generarse_mas_grandes(self) -> None:
        escena = EscenaNivel1(self.gestor)
        volcan = escena._volcanes[0]
        pantalla = pygame.Surface((100, 100))
        burbuja = Burbuja(50, 50, 100, 10, 10)

        burbuja.dibujar(pantalla)

        self.assertEqual(
            pantalla.get_at((burbuja.hurtbox.centerx, burbuja.hurtbox.centery))[:3],
            Burbuja.COLOR_RELLENO,
        )
        with (
            patch("Entidades.random.random", return_value=0.0),
            patch("Entidades.random.randint", return_value=18),
        ):
            volcan._crear_burbuja()

        self.assertEqual(volcan.burbujas[-1].radio, 18)
        self.assertGreater(
            volcan.burbujas[-1].radio,
            volcan.RADIO_BURBUJA_PEQUENA[1],
        )

    def test_colision_con_burbuja_resta_salud_y_consume_el_proyectil(self) -> None:
        escena = EscenaNivel1(self.gestor)
        volcan = escena._volcanes[0]
        volcan._tiempo_hasta_burbuja = 10
        burbuja = Burbuja(
            x=escena._jugador.hurtbox.centerx,
            y=escena._jugador.hurtbox.centery,
            velocidad=150,
            radio=8,
            danio=volcan.DANIO_BURBUJA,
        )
        volcan.burbujas.append(burbuja)

        escena.actualizar(0)

        self.assertEqual(escena._jugador.salud.vida_actual, 90)
        self.assertEqual(escena._jugador.temporizador_invulnerable, 1.0)
        self.assertNotIn(burbuja, volcan.burbujas)

    def test_cambiar_a_escena_no_registrada_informa_error(self) -> None:
        gestor_sin_escenas = GestorEscenas()

        with self.assertRaises(KeyError):
            gestor_sin_escenas.cambiar_escena(EstadoEscena.MENU)

    def test_componente_salud_resta_danio_y_detecta_si_sigue_vivo(self) -> None:
        salud = ComponenteSalud(100)

        salud.recibir_danio(35)

        self.assertEqual(salud.vida_actual, 65)
        self.assertTrue(salud.esta_vivo())

    def test_componente_salud_no_permite_vida_negativa(self) -> None:
        salud = ComponenteSalud(20)

        salud.recibir_danio(30)

        self.assertEqual(salud.vida_actual, 0)
        self.assertFalse(salud.esta_vivo())

    def test_componente_salud_rechaza_valores_invalidos(self) -> None:
        with self.assertRaises(ValueError):
            ComponenteSalud(0)

        salud = ComponenteSalud(50)
        with self.assertRaises(ValueError):
            salud.recibir_danio(-1)

    def test_jugador_inicializa_su_componente_salud(self) -> None:
        jugador = Jugador(0, 0, vida_inicial=80)

        self.assertIsInstance(jugador.salud, ComponenteSalud)
        self.assertEqual(jugador.salud.vida_actual, 80)

    def test_dron_recuperador_tiene_hurtbox_del_tamano_visual(self) -> None:
        jugador = Jugador(100, 100)

        self.assertEqual(jugador.hitbox.size, (Jugador.ANCHO, Jugador.ALTO))
        self.assertEqual(jugador.hurtbox, jugador.hitbox)
        pantalla = pygame.Surface((300, 300))
        jugador.dibujar(pantalla)
        pixeles_dron = [
            (x, y)
            for x in range(pantalla.get_width())
            for y in range(pantalla.get_height())
            if pantalla.get_at((x, y))[:3] != (0, 0, 0)
        ]
        self.assertTrue(pixeles_dron)
        self.assertTrue(
            all(
                jugador.hurtbox.left <= x < jugador.hurtbox.right
                and jugador.hurtbox.top <= y < jugador.hurtbox.bottom
                for x, y in pixeles_dron
            )
        )

    def test_jugador_tiene_hurtbox_sin_generar_attackbox(self) -> None:
        jugador = Jugador(100, 100)

        self.assertEqual(jugador.hurtbox, jugador.hitbox)
        jugador.x += 20
        jugador.actualizar_hitbox()
        self.assertEqual(jugador.hurtbox, jugador.hitbox)
        self.assertFalse(hasattr(jugador, "attackbox"))

    def test_los_tres_volcanes_danan_por_contacto_y_respetan_invulnerabilidad(
        self,
    ) -> None:
        escena = EscenaNivel1(self.gestor)
        salud_esperada = 100
        for indice, volcan in enumerate(escena._volcanes):
            if indice:
                escena._jugador.temporizador_invulnerable = 0.0
            escena._jugador.x = volcan.x + (volcan.ancho - escena._jugador.ancho) / 2
            escena._jugador.y = volcan.y + (volcan.alto - escena._jugador.alto) / 2
            escena._jugador.actualizar_hitbox()
            escena.actualizar(0)

            salud_esperada -= volcan.DANIO_CONTACTO
            self.assertTrue(escena._jugador.hurtbox.colliderect(volcan.hurtbox))
            self.assertEqual(escena._jugador.salud.vida_actual, salud_esperada)
            self.assertEqual(escena._jugador.temporizador_invulnerable, 1.0)
            escena.actualizar(0)
            self.assertEqual(escena._jugador.salud.vida_actual, salud_esperada)

        escena._jugador.actualizar(0.5)
        self.assertAlmostEqual(escena._jugador.temporizador_invulnerable, 0.5)
        escena._jugador.actualizar(0.5)
        self.assertEqual(escena._jugador.temporizador_invulnerable, 0.0)

    def test_fin_de_partida_congela_el_nivel_y_enter_reinicia(self) -> None:
        escena = self.escena_nivel
        self.gestor.cambiar_escena(EstadoEscena.JUEGO)
        escena._jugador.salud.vida_actual = 10
        escena._intentar_daniar_jugador(10, "Daño de prueba.")
        posicion_pez = escena._peces[0].x
        posicion_residuo = escena._residuos[0].rectangulo.copy()

        escena.actualizar(0.5)

        self.assertTrue(escena._partida_terminada)
        self.assertEqual(escena._peces[0].x, posicion_pez)
        self.assertEqual(escena._residuos[0].rectangulo, posicion_residuo)
        pantalla = pygame.Surface((1280, 720))
        escena.dibujar(pantalla)
        self.assertNotEqual(pantalla.get_at((0, 0))[:3], COLOR_FONDO)

        escena.manejar_evento(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        )

        self.assertFalse(escena._partida_terminada)
        self.assertEqual(escena._jugador.salud.vida_actual, 100)
        self.assertEqual(escena.calidad_agua, escena.CALIDAD_INICIAL)
        self.assertEqual(len(escena._residuos), 10)

        escena._jugador.salud.vida_actual = 1
        escena._intentar_daniar_jugador(1, "Daño de prueba.")
        escena.manejar_evento(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        )
        self.assertIsInstance(self.gestor.escena_actual, EscenaMenu)

    def test_escape_y_comenzar_desde_menu_inicia_partida_nueva(self) -> None:
        escena = self.escena_nivel
        self.gestor.cambiar_escena(EstadoEscena.JUEGO)
        escena._calidad_agua = 70
        escena._jugador.salud.vida_actual = 40

        escena.manejar_evento(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
        )
        self.gestor.manejar_evento(
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        )

        self.assertIs(self.gestor.escena_actual, escena)
        self.assertEqual(escena.calidad_agua, escena.CALIDAD_INICIAL)
        self.assertEqual(escena._jugador.salud.vida_actual, 100)
        self.assertEqual(len(escena._residuos), 10)

    def test_jugador_se_mueve_con_flechas_y_delta_time(self) -> None:
        escena = EscenaNivel1(self.gestor)
        escena._jugador.x = 100.0
        escena._jugador.y = 200.0
        escena._jugador.actualizar_hitbox()

        keys = {
            pygame.K_RIGHT: True,
            pygame.K_DOWN: True,
        }

        escena._jugador.actualizar_con_teclas(keys, 0.5)

        desplazamiento_x = escena._jugador.x - 100.0
        desplazamiento_y = escena._jugador.y - 200.0
        distancia = math.hypot(desplazamiento_x, desplazamiento_y)

        self.assertAlmostEqual(distancia, escena._jugador.velocidad_submarina * 0.5)
        self.assertAlmostEqual(desplazamiento_x, desplazamiento_y)
        self.assertEqual(escena._jugador.hitbox.x, int(escena._jugador.x))
        self.assertEqual(escena._jugador.hitbox.y, int(escena._jugador.y))

    def test_recoger_residuo_mejora_calidad_del_agua(self) -> None:
        escena = EscenaNivel1(self.gestor)
        calidad_inicial = escena.calidad_agua
        color_inicial = escena._color_agua()
        colores_peces_iniciales = [pez.color for pez in escena._peces]
        residuo = escena._residuos[0]
        escena._jugador.x = residuo.rectangulo.centerx - escena._jugador.ancho // 2
        escena._jugador.y = residuo.rectangulo.centery - escena._jugador.alto // 2
        escena._jugador.actualizar_hitbox()

        escena.actualizar(0)

        self.assertEqual(
            escena.calidad_agua,
            calidad_inicial
            + (escena.CALIDAD_MAXIMA - escena.CALIDAD_INICIAL)
            // escena._total_residuos,
        )
        self.assertNotEqual(escena._color_agua(), color_inicial)
        self.assertTrue(
            all(
                pez.color != color_inicial_pez
                for pez, color_inicial_pez in zip(
                    escena._peces,
                    colores_peces_iniciales,
                )
            )
        )
        self.assertNotIn(residuo, escena._residuos)
        self.assertIn("calidad", escena._mensaje.lower())

    def test_hay_diez_residuos_y_se_mueven_levemente_con_la_corriente(self) -> None:
        escena = EscenaNivel1(self.gestor)
        posiciones_iniciales = [
            residuo.rectangulo.topleft for residuo in escena._residuos
        ]

        self.assertEqual(len(escena._residuos), 10)
        self.assertTrue(
            all(isinstance(residuo, ResiduoFlotante) for residuo in escena._residuos)
        )
        escena.actualizar(1.0)

        desplazamientos = [
            (
                abs(residuo.rectangulo.x - x_inicial),
                abs(residuo.rectangulo.y - y_inicial),
            )
            for residuo, (x_inicial, y_inicial) in zip(
                escena._residuos,
                posiciones_iniciales,
            )
        ]
        self.assertTrue(any(x or y for x, y in desplazamientos))
        self.assertTrue(
            all(
                x <= ResiduoFlotante.AMPLITUD_HORIZONTAL * 2
                and y <= ResiduoFlotante.AMPLITUD_VERTICAL * 2
                for x, y in desplazamientos
            )
        )

    def test_flora_aparece_progresivamente_y_se_dibuja_al_limpiar(self) -> None:
        escena = EscenaNivel1(self.gestor)
        pantalla = pygame.Surface((1280, 720))

        self.assertTrue(all(isinstance(planta, PlantaAcuatica) for _, planta in escena._flora))
        self.assertEqual(
            sum(escena.calidad_agua >= minimo for minimo, _ in escena._flora),
            0,
        )

        residuo = escena._residuos[0]
        escena._jugador.x = residuo.rectangulo.centerx - escena._jugador.ancho // 2
        escena._jugador.y = residuo.rectangulo.centery - escena._jugador.alto // 2
        escena._jugador.actualizar_hitbox()
        escena.actualizar(0)
        residuo = escena._residuos[0]
        escena._jugador.x = residuo.rectangulo.centerx - escena._jugador.ancho // 2
        escena._jugador.y = residuo.rectangulo.centery - escena._jugador.alto // 2
        escena._jugador.actualizar_hitbox()
        escena.actualizar(0)

        self.assertEqual(
            sum(escena.calidad_agua >= minimo for minimo, _ in escena._flora),
            2,
        )
        escena.dibujar(pantalla)
        primera_planta = escena._flora[0][1]
        self.assertTrue(
            any(
                pantalla.get_at((x, y))[:3] == primera_planta.color
                for x in range(75, 115)
                for y in range(escena._suelo.top - primera_planta.altura, escena._suelo.top)
            )
        )

    def test_recoger_todos_los_residuos_deja_el_agua_saludable(self) -> None:
        escena = EscenaNivel1(self.gestor)
        pantalla = pygame.Surface((1280, 720))

        escena.dibujar(pantalla)
        self.assertEqual(
            pantalla.get_at((0, escena._suelo.top + 10))[:3],
            escena.COLOR_SUELO_CONTAMINADO,
        )

        for cantidad_recogida, residuo in enumerate(
            escena._residuos[:],
            start=1,
        ):
            escena._jugador.x = residuo.rectangulo.centerx - escena._jugador.ancho // 2
            escena._jugador.y = residuo.rectangulo.centery - escena._jugador.alto // 2
            escena._jugador.actualizar_hitbox()
            escena.actualizar(0)
            self.assertEqual(
                escena.calidad_agua,
                escena.CALIDAD_INICIAL
                + (escena.CALIDAD_MAXIMA - escena.CALIDAD_INICIAL)
                * cantidad_recogida
                // escena._total_residuos,
            )

        escena.dibujar(pantalla)

        self.assertEqual(escena.calidad_agua, 100)
        self.assertEqual(escena._color_agua(), escena.COLOR_AGUA_LIMPIA)
        self.assertEqual(
            pantalla.get_at((0, escena._suelo.top + 10))[:3],
            escena.COLOR_SUELO_MUSGO,
        )
        self.assertEqual(
            sum(escena.calidad_agua >= minimo for minimo, _ in escena._flora),
            len(escena._flora),
        )
        self.assertTrue(
            all(
                pez.color == pez._color_final
                for pez in escena._peces
            )
        )
        self.assertEqual(pantalla.get_at((0, 0))[:3], COLOR_FONDO)
        self.assertEqual(
            pantalla.get_at((0, escena.LIMITE_SUPERIOR_LAGUNA))[:3],
            escena.COLOR_AGUA_LIMPIA,
        )

    def test_pez_movil_dania_al_jugador_pero_puede_seguir_limpiando(self) -> None:
        escena = EscenaNivel1(self.gestor)
        calidad_inicial = escena.calidad_agua
        pez = escena._peces[0]
        escena._jugador.x = pez.x
        escena._jugador.y = pez.y
        escena._jugador.actualizar_hitbox()

        escena.actualizar(0)

        self.assertEqual(escena._jugador.salud.vida_actual, 100 - pez.DANIO)
        self.assertIn("pez", escena._mensaje.lower())

        residuo = escena._residuos[0]
        escena._jugador.x = residuo.rectangulo.centerx - escena._jugador.ancho // 2
        escena._jugador.y = residuo.rectangulo.centery - escena._jugador.alto // 2
        escena._jugador.actualizar_hitbox()
        escena.actualizar(0)

        self.assertGreater(escena.calidad_agua, calidad_inicial)

    def test_jugador_queda_dentro_de_los_limites_del_mapa(self) -> None:
        escena = EscenaNivel1(self.gestor)
        escena._jugador.x = 10000.0
        escena._jugador.y = 10000.0

        escena.actualizar(1 / 60)

        self.assertLessEqual(escena._jugador.hitbox.right, ANCHO_VENTANA)
        self.assertLessEqual(escena._jugador.hitbox.bottom, escena._suelo.top)
        self.assertGreaterEqual(escena._jugador.hitbox.left, 0)
        self.assertGreaterEqual(escena._jugador.hitbox.top, 0)


if __name__ == "__main__":
    unittest.main()
