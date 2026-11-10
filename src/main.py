"""Punto de entrada y bucle principal de Guardianes del Agua."""

import sys
from pathlib import Path

import pygame

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import ALTO_VENTANA, ANCHO_VENTANA, FPS, TITULO_VENTANA
from src.escenas.escena_menu import EscenaMenu
from src.escenas.escena_nivel_1 import EscenaNivel1
from src.gestor_escenas import EstadoEscena, GestorEscenas


def crear_gestor_escenas() -> GestorEscenas:
    """Construye y configura las escenas disponibles del juego."""
    gestor_escenas = GestorEscenas()
    gestor_escenas.registrar_escena(
        EstadoEscena.MENU,
        EscenaMenu(gestor_escenas),
    )
    gestor_escenas.registrar_escena(
        EstadoEscena.JUEGO,
        EscenaNivel1(gestor_escenas),
    )
    gestor_escenas.cambiar_escena(EstadoEscena.MENU)
    return gestor_escenas


def main() -> None:
    """Inicializa Pygame y ejecuta el game loop hasta cerrar la ventana."""
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
    pygame.display.set_caption(TITULO_VENTANA)

    reloj = pygame.time.Clock()
    gestor_escenas = crear_gestor_escenas()
    ejecutando = True

    try:
        while ejecutando:
            delta_time = min(reloj.tick(FPS) / 1000.0, 0.1)

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False
                else:
                    gestor_escenas.manejar_evento(evento)

            if ejecutando:
                gestor_escenas.actualizar(delta_time)
                gestor_escenas.dibujar(pantalla)
                pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
