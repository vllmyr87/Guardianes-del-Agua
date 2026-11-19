# Guardianes del Agua

Prototipo educativo 2D creado con Python y Pygame. En el primer nivel, el
jugador pilota un dron submarino recuperador y recoge residuos para mejorar la
calidad del agua de una laguna.

## Requisitos

- Python 3.10 o posterior.
- pip, incluido normalmente con Python.

## Instalación

Abre una terminal en la carpeta `33_Proyecto Guardianes del Agua` y crea un
entorno virtual:

```powershell
py -m venv .venv
```

Actívalo en Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

En macOS o Linux, actívalo con:

```sh
source .venv/bin/activate
```

Instala las dependencias del proyecto:

```sh
python -m pip install -r requirements.txt
```

## Ejecución

Desde la carpeta del proyecto, con el entorno virtual activado, ejecuta:

```sh
python -m src.main
```

Se abrirá una ventana de 1280 × 720 píxeles.

## Controles

### Menú

- **Enter** o **barra espaciadora**: comenzar.
- **Clic izquierdo** en el botón **Comenzar**: comenzar.

### Nivel

- **Flechas** o **W/A/S/D**: mover al personaje.
- Recoge los diez residuos, que flotan suavemente con la corriente, para
  aumentar la calidad del agua.
- A medida que mejora la calidad del agua, crecen plantas acuáticas en el fondo
  y los peces recuperan colores vivos; el suelo submarino pasa gradualmente de
  un tono oscuro a verde musgo.
- Esquiva los peces móviles y los tres volcanes del fondo: tocarlos o recibir
  sus burbujas resta salud.
- Las burbujas grises contaminantes suben en línea recta, tienen tamaños
  variables y desaparecen al llegar a la superficie.
- Tras recibir daño, tienes un segundo de invulnerabilidad.
- Si la salud llega a cero, la partida se congela: pulsa **Enter** para
  reiniciar el nivel o **Escape** para volver al menú. **Comenzar** siempre
  inicia una partida nueva.
- **Escape**: volver al menú.
- Cerrar la ventana: salir del juego.

El medidor y el color del agua muestran su estado: contaminada, en recuperación
y saludable. A medida que se limpia, brotan plantas acuáticas de distintos
tamaños y los peces recuperan sus colores. Los mensajes dan retroalimentación
al recoger residuos o recibir daño; puedes seguir limpiando después de un error.

## Ejecutar las pruebas

Desde la carpeta del proyecto, ejecuta:

```sh
python -m unittest discover -s tests -v
```
