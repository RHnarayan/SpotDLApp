from cx_Freeze import setup, Executable
import os

# Rutas absolutas de los archivos necesarios
app_path = r"C:\Users\artik\Documents\spotdl\gui_spotdl.py"  # Ruta al archivo principal
ffmpeg_path = r"C:\Users\artik\ffmpeg-2024-11-11-git-96d45c3b21-full_build\bin"  # Ruta a la carpeta de FFmpeg
venv_path = r"C:\Users\artik\Documents\spotdl\venv\Lib\site-packages"  # Ruta al site-packages del entorno virtual

# Archivos adicionales a incluir en el build
include_files = [
    os.path.join(ffmpeg_path, "ffmpeg.exe"),  # FFmpeg binario
    os.path.join(ffmpeg_path, "ffprobe.exe"),  # FFprobe binario
    os.path.join(os.path.dirname(app_path), "spotdl.exe"),  # Incluir spotdl.exe en la carpeta compilada
    os.path.join(os.path.dirname(app_path), "config.ini"),  # Incluir el archivo de configuración .ini
    (venv_path, "site-packages"),  # Incluir las dependencias del entorno virtual
]

# Opciones para la construcción del ejecutable
build_exe_options = {
    'packages': ['wx', 'threading', 'subprocess', 're', 'os', 'ctypes', 'logging', 'configparser'],  # Paquetes usados en el código
    'include_files': include_files,  # Archivos adicionales
    'excludes': ['tkinter'],  # Excluir tkinter si no es necesario
    'optimize': 2,  # Optimización del bytecode para reducir tamaño
    'bin_includes': ['ffmpeg.exe', 'ffprobe.exe'],  # Incluir archivos binarios de FFmpeg
}

# Configuración del ejecutable principal
executables = [
    Executable(
        app_path,
        base="Win32GUI",  # Cambiar a None si es una aplicación de consola
        target_name="SpotDLApp.exe",
        icon=None  # Cambia esto por un icono si tienes uno
    )
]

# Configuración para cx_Freeze
setup(
    name="SpotDLApp",
    version="1.4",
    description="Aplicación de descarga de música desde Spotify",
    options={'build_exe': build_exe_options},
    executables=executables
)
