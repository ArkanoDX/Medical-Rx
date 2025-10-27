import sys
import os  # <-- ¡Importante! Lo necesitamos para las rutas
# Importamos los módulos necesarios de PyQt5
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QWidget,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap

# Importamos las funciones del modelo que creamos
# (Usamos '..' para subir un nivel desde 'gui/' a la raíz 'Medical_Rx/')
import model.base_datos as db

# --- Definimos la ruta base para encontrar los assets ---
# Esto es para que funcione sin importar desde dónde ejecutes el script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class VentanaLogin(QDialog):
    """
    Ventana de diálogo para el inicio de sesión.
    Emite una señal 'login_exitoso' con los datos del doctor si la validación es correcta.
    """

    login_exitoso = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- 1. Configuración de la Ventana ---
        self.setWindowTitle("Medical Rx - Inicio de Sesión")
        self.setFixedSize(400, 550)

        # --- 2. Hacemos la ventana "flotante" (sin marco) ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # --- 3. Inicializar UI y Estilos ---
        self.init_ui()
        self.init_style()

    def init_ui(self):
        """Crea los widgets (botones, campos de texto, etc.)"""

        # --- 1. Creamos la "Tarjeta" de fondo ---
        self.fondo_tarjeta = QFrame(self)
        self.fondo_tarjeta.setObjectName("FondoTarjeta")

        # --- 2. Widgets de la interfaz ---

        # --- (NUEVO) Widget para la imagen del Avatar ---
        self.etiqueta_avatar = QLabel()
        self.etiqueta_avatar.setAlignment(Qt.AlignCenter)
        ruta_avatar = os.path.join(BASE_DIR, 'assets', 'images', 'avatar.png')

        avatar_pixmap = QPixmap(ruta_avatar)
        if avatar_pixmap.isNull():
            print(f"Advertencia: No se pudo cargar la imagen en {ruta_avatar}")
            # Opcional: poner un texto si no se encuentra la imagen
            self.etiqueta_avatar.setText("[ IMAGEN ]")
        else:
            # Escalamos la imagen a 100x100 px, manteniendo la proporción
            self.etiqueta_avatar.setPixmap(avatar_pixmap.scaled(
                100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

        # --- Título (como ya estaba) ---
        self.etiqueta_titulo = QLabel("INICIO DE SESIÓN")
        self.etiqueta_titulo.setObjectName("Titulo")
        self.etiqueta_titulo.setAlignment(Qt.AlignCenter)

        # Campos de texto (QLineEdit)
        self.campo_usuario = QLineEdit()
        self.campo_usuario.setPlaceholderText("Usuario")

        self.campo_contrasena = QLineEdit()
        self.campo_contrasena.setPlaceholderText("Contraseña")
        self.campo_contrasena.setEchoMode(QLineEdit.Password)  # Oculta la contraseña

        # Botón de Login
        self.boton_login = QPushButton("INGRESAR")
        self.boton_login.setObjectName("BotonLogin")

        # Botón para cerrar
        self.boton_cerrar = QPushButton("X")
        self.boton_cerrar.setObjectName("BotonCerrar")

        # --- 3. Creamos el Layout (Organización) ---

        layout_tarjeta = QVBoxLayout(self.fondo_tarjeta)
        layout_tarjeta.setContentsMargins(40, 40, 40, 40)
        layout_tarjeta.setSpacing(20)

        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(self.fondo_tarjeta)

        self.boton_cerrar.setFixedSize(30, 30)
        self.boton_cerrar.move(360, 10)
        self.boton_cerrar.setParent(self)

        # --- (MODIFICADO) Añadimos widgets al layout ---
        # El orden ahora es:
        # [Espacio] -> Imagen -> Título -> Campos -> Botón -> [Espacio]

        layout_tarjeta.addStretch()  # Añade espacio flexible arriba

        layout_tarjeta.addWidget(self.etiqueta_avatar)  # Imagen de avatar
        layout_tarjeta.addSpacing(10)  # Espacio pequeño entre imagen y título
        layout_tarjeta.addWidget(self.etiqueta_titulo)
        layout_tarjeta.addSpacing(30)  # Espacio más grande

        layout_tarjeta.addWidget(self.campo_usuario)
        layout_tarjeta.addWidget(self.campo_contrasena)
        layout_tarjeta.addSpacing(30)

        layout_tarjeta.addWidget(self.boton_login)
        layout_tarjeta.addStretch()  # Añade espacio flexible abajo

        self.setLayout(layout_principal)

        # --- 4. Conexión de Señales (Eventos) ---
        self.boton_login.clicked.connect(self._on_login_clicked)
        self.boton_cerrar.clicked.connect(self.reject)

    def init_style(self):
        """Aplica la hoja de estilos QSS (el "CSS")"""

        color_base = "#90d5ff"
        color_fondo = "#FFFFFF"
        color_boton = "#007bff"
        color_boton_hover = "#0056b3"
        color_texto_principal = "#333"
        color_placeholder = "#999"
        color_borde = "#ddd"

        qss = f"""
            #FondoTarjeta {{
                background-color: {color_fondo};
                border-radius: 20px; 
                border: 1px solid {color_borde};
            }}

            /* --- (MODIFICADO) Título "INICIAR SESIÓN" --- */
            #Titulo {{
                font-size: 20px; /* Reducido de 24px */
                font-weight: bold;
                color: {color_texto_principal};
            }}

            QLineEdit {{
                font-size: 16px;
                padding: 12px;
                border: 1px solid {color_borde};
                border-radius: 8px;
                color: {color_texto_principal};
            }}
            QLineEdit::placeholder {{
                color: {color_placeholder};
            }}

            #BotonLogin {{
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: {color_boton};
                padding: 12px;
                border: none;
                border-radius: 8px;
            }}
            #BotonLogin:hover {{
                background-color: {color_boton_hover};
            }}

            #BotonCerrar {{
                font-size: 14px;
                font-weight: bold;
                color: #AAA;
                background-color: transparent;
                border: none;
                border-radius: 15px;
            }}
            #BotonCerrar:hover {{
                background-color: #EEE;
                color: #555;
            }}
        """
        self.setStyleSheet(qss)

    def _on_login_clicked(self):
        """
        Lógica que se ejecuta al presionar 'INGRESAR'.
        """
        usuario = self.campo_usuario.text()
        contrasena = self.campo_contrasena.text()

        if not usuario or not contrasena:
            QMessageBox.warning(self, "Error", "Debes ingresar un usuario y una contraseña.")
            return

        doctor_data = db.validar_doctor(usuario, contrasena)

        if doctor_data:
            self.login_exitoso.emit(doctor_data)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Usuario o contraseña incorrectos.")

    # --- Funciones para poder mover la ventana (ya que no tiene marco) ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()


# --- Bloque para probar esta ventana de forma independiente ---
if __name__ == "__main__":
    # Importante: Registramos un doctor de prueba si no existe
    if not db.validar_doctor("dr_prueba", "101010"):  # (Cambié la pass de prueba por si acaso)
        db.registrar_doctor(
            "dr_prueba",
            "101010",
            "Dr. Juan Pérez",
            "12345678",
            "Cardiología",
            "UNAM",
            "Calle Falsa 123",
            "55-1234-5678"
        )

    app = QApplication(sys.argv)
    ventana = VentanaLogin()

    ventana.login_exitoso.connect(lambda data: print(f"Login exitoso para: {data['nombre_completo']}"))

    ventana.show()
    sys.exit(app.exec_())