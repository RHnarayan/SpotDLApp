import wx
import threading
import subprocess
import logging
import configparser
import os
import sys

# Configuración de logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SpotDLApp(wx.Frame):
    def __init__(self, parent, title):
        super(SpotDLApp, self).__init__(parent, title=title, size=(900, 700))

        # Cargar configuraciones desde el archivo .ini
        self.config = self.load_config()

        self.output_dir = self.config.get('general', 'output_dir', fallback="./downloads")
        self.format = self.config.get('general', 'format', fallback="mp3")
        self.bitrate = self.config.get('general', 'bitrate', fallback="320k")
        self.audio_provider = self.config.get('general', 'audio_provider', fallback="youtube-music")

        self.init_ui()
        self.Centre()
        self.Show()

    def load_config(self):
        config = configparser.ConfigParser()

        # Verificar si el archivo de configuración existe, si no, lo creamos con valores predeterminados
        config_file = 'config.ini'
        if not os.path.exists(config_file):
            self.create_default_config(config)

        config.read(config_file)
        return config

    def create_default_config(self, config):
        """Crear una configuración predeterminada si el archivo .ini no existe."""
        if not config.has_section('general'):
            config.add_section('general')
        config.set('general', 'output_dir', './downloads')
        config.set('general', 'format', 'mp3')
        config.set('general', 'bitrate', '320k')
        config.set('general', 'audio_provider', 'youtube-music')

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def save_config(self):
        # Asegurarse de que las secciones existan
        if not self.config.has_section('general'):
            self.config.add_section('general')
        self.config.set('general', 'output_dir', self.output_dir)
        self.config.set('general', 'format', self.format)
        self.config.set('general', 'bitrate', self.bitrate)
        self.config.set('general', 'audio_provider', self.audio_provider)

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Título
        title_label = wx.StaticText(panel, label="SpotDL - Descarga Personalizable de Spotify")
        title_label.SetFont(wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        main_sizer.Add(title_label, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Entrada de URL
        url_label = wx.StaticText(panel, label="URL de Spotify:")
        main_sizer.Add(url_label, flag=wx.LEFT | wx.TOP, border=10)
        self.url_input = wx.TextCtrl(panel)
        main_sizer.Add(self.url_input, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        # Botón para pegar contenido del portapapeles
        paste_button = wx.Button(panel, label="Pegar URL")
        paste_button.Bind(wx.EVT_BUTTON, self.on_paste_url)
        main_sizer.Add(paste_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Formato de salida
        format_label = wx.StaticText(panel, label="Formato de Salida:")
        main_sizer.Add(format_label, flag=wx.LEFT | wx.TOP, border=10)
        self.format_combobox = wx.ComboBox(panel, choices=["mp3", "flac", "ogg", "opus", "m4a", "wav"], style=wx.CB_READONLY)
        self.format_combobox.SetValue(self.format)
        main_sizer.Add(self.format_combobox, flag=wx.LEFT | wx.RIGHT, border=10)

        # Bitrate
        bitrate_label = wx.StaticText(panel, label="Bitrate:")
        main_sizer.Add(bitrate_label, flag=wx.LEFT | wx.TOP, border=10)
        self.bitrate_combobox = wx.ComboBox(panel, choices=["auto", "disable"] + [f"{i}k" for i in range(8, 321, 8)], style=wx.CB_READONLY)
        self.bitrate_combobox.SetValue(self.bitrate)
        main_sizer.Add(self.bitrate_combobox, flag=wx.LEFT | wx.RIGHT, border=10)

        # Botón para seleccionar carpeta de descargas
        dir_button = wx.Button(panel, label="Seleccionar Carpeta de Descargas")
        dir_button.Bind(wx.EVT_BUTTON, self.on_select_directory)
        main_sizer.Add(dir_button, flag=wx.ALIGN_CENTER | wx.ALL, border=10)

        # Mostrar carpeta de descargas seleccionada
        self.dir_display = wx.StaticText(panel, label=f"Carpeta de descargas: {self.output_dir}")
        main_sizer.Add(self.dir_display, flag=wx.LEFT | wx.TOP, border=10)

        # Botón para iniciar descarga
        download_button = wx.Button(panel, label="Iniciar Descarga")
        download_button.Bind(wx.EVT_BUTTON, self.on_download)
        main_sizer.Add(download_button, flag=wx.ALIGN_CENTER | wx.ALL, border=20)

        # Estado
        self.status_label = wx.StaticText(panel, label="Estado: Esperando URL")
        main_sizer.Add(self.status_label, flag=wx.LEFT | wx.TOP, border=10)

        # Botón para guardar la configuración
        save_button = wx.Button(panel, label="Guardar Configuración")
        save_button.Bind(wx.EVT_BUTTON, self.on_save_config)
        main_sizer.Add(save_button, flag=wx.ALIGN_CENTER | wx.ALL, border=20)

        panel.SetSizer(main_sizer)

    def on_paste_url(self, event):
        """Pegar el contenido del portapapeles en el campo de texto"""
        if wx.TheClipboard.Open():
            if wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
                data_object = wx.TextDataObject()
                wx.TheClipboard.GetData(data_object)
                self.url_input.SetValue(data_object.GetText())
            wx.TheClipboard.Close()

    def on_save_config(self, event):
        """Guardar configuración en el archivo .ini"""
        self.output_dir = self.dir_display.GetLabel().split(": ")[1]
        self.format = self.format_combobox.GetValue()
        self.bitrate = self.bitrate_combobox.GetValue()

        # Guardar en el archivo .ini
        self.save_config()
        wx.MessageBox("Configuración guardada correctamente.", "Éxito", wx.OK | wx.ICON_INFORMATION)

    def on_select_directory(self, event):
        dlg = wx.DirDialog(self, "Selecciona un directorio de descargas", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.output_dir = dlg.GetPath()
            self.dir_display.SetLabel(f"Carpeta de descargas: {self.output_dir}")
        dlg.Destroy()

    def on_download(self, event):
        url = self.url_input.GetValue().strip()
        if not url:
            wx.MessageBox("Por favor, ingrese una URL válida.", "Error", wx.OK | wx.ICON_ERROR)
            return

        self.status_label.SetLabel("Estado: Iniciando descarga...")
        threading.Thread(target=self.start_download, args=(url,), daemon=True).start()

    def start_download(self, url):
        try:
            # Ruta absoluta al binario spotdl.exe
            if getattr(sys, 'frozen', False):
                # Si la aplicación está compilada
                spotdl_exe = os.path.join(sys._MEIPASS, "spotdl.exe")
            else:
                # Si estamos ejecutando desde el entorno de desarrollo
                spotdl_exe = os.path.join(os.path.dirname(__file__), "spotdl.exe")

            logging.debug(f"Ruta calculada para spotdl.exe: {spotdl_exe}")
            logging.debug(f"Comprobando existencia de spotdl.exe: {os.path.exists(spotdl_exe)}")

            # Verificar si spotdl.exe existe
            if not os.path.exists(spotdl_exe):
                logging.error(f"El archivo spotdl.exe no se encuentra en la ruta: {spotdl_exe}")
                wx.CallAfter(wx.MessageBox, f"El archivo spotdl.exe no se encontró en: {spotdl_exe}", "Error", wx.OK | wx.ICON_ERROR)
                return

            command = [
                spotdl_exe,
                "--audio", self.audio_provider,
                "--format", self.format,
                "--bitrate", self.bitrate,
                "--output", self.output_dir,
                url
            ]

            logging.debug(f"Comando ejecutado: {' '.join(command)}")

            # Ejecutar el comando
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            logging.info(f"Descarga completada: {result.stdout}")
            wx.CallAfter(self.status_label.SetLabel, "Estado: Descarga completada.")
            wx.CallAfter(self.show_open_folder_dialog)

        except FileNotFoundError as e:
            logging.error(f"No se encontró el archivo: {e}")
            wx.CallAfter(self.status_label.SetLabel, "Estado: Error - Archivo no encontrado.")
            wx.CallAfter(wx.MessageBox, f"No se encontró el archivo: {e}", "Error", wx.OK | wx.ICON_ERROR)

        except subprocess.CalledProcessError as e:
            logging.error(f"Error en la descarga: {e.stderr}")
            wx.CallAfter(self.status_label.SetLabel, "Estado: Error en la descarga.")
            wx.CallAfter(wx.MessageBox, f"Error en la descarga: {e.stderr}", "Error", wx.OK | wx.ICON_ERROR)

    def show_open_folder_dialog(self):
        """Mostrar cuadro de diálogo para abrir la carpeta después de la descarga"""
        open_folder_dialog = wx.MessageDialog(self, "¿Deseas abrir la carpeta de descargas?", "Abrir Carpeta", 
                                              wx.YES_NO | wx.ICON_QUESTION)
        if open_folder_dialog.ShowModal() == wx.ID_YES:
            self.on_open_download_folder()

    def on_open_download_folder(self):
        """Abrir la carpeta de descargas en el explorador de archivos"""
        try:
            result = subprocess.run(['explorer', self.output_dir])
            if result.returncode != 0:
                logging.warning(f"Comando 'explorer' terminó con un código de salida inesperado: {result.returncode}")
        except Exception as e:
            logging.error(f"Error al abrir la carpeta: {e}")
            wx.MessageBox(f"Error al abrir la carpeta de descargas: {e}", "Error", wx.OK | wx.ICON_ERROR)

if __name__ == "__main__":
    app = wx.App()
    SpotDLApp(None, title="SpotDL GUI - Descargas Spotify")
    app.MainLoop()
