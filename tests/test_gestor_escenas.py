"""Pruebas del cambio de estado y del flujo inicial del menú."""

import unittest

import pygame

from src.escenas.escena_juego import EscenaJuego
from src.escenas.escena_menu import EscenaMenu
from src.config import COLOR_FONDO
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
        self.gestor.registrar_escena(EstadoEscena.JUEGO, EscenaJuego(self.gestor))
        self.gestor.cambiar_escena(EstadoEscena.MENU)

    def test_tecla_enter_inicia_el_juego(self) -> None:
        evento = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)

        self.gestor.manejar_evento(evento)

        self.assertIsInstance(self.gestor.escena_actual, EscenaJuego)

    def test_clic_en_comenzar_inicia_el_juego(self) -> None:
        evento = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=(640, 430),
        )

        self.gestor.manejar_evento(evento)

        self.assertIsInstance(self.gestor.escena_actual, EscenaJuego)

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

    def test_cambiar_a_escena_no_registrada_informa_error(self) -> None:
        gestor_sin_escenas = GestorEscenas()

        with self.assertRaises(KeyError):
            gestor_sin_escenas.cambiar_escena(EstadoEscena.MENU)


if __name__ == "__main__":
    unittest.main()
