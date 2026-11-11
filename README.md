# StudyMate - Aplicación Móvil Académica

Aplicación móvil desarrollada en **Python 3.10.5** y **Kivy 2.3.0** para la gestión académica integral de estudiantes universitarios (seguimiento de calificaciones, cálculo predictivo de aprobación, horario semanal interactivo, importación de horarios por foto/OCR, diario de reflexión, recordatorios y analítica de progreso).

---

## 🚀 Requisitos previos

* **Python 3.10.5**
* **Git**
* Entorno virtual de Python configurado

---

## 🛠️ Guía de instalación y ejecución

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/jeancarlos-arch/StudyMate.git
   cd StudyMate
   ```

2. **Crear y activar el entorno virtual:**
   * En Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   * En Windows (CMD):
     ```cmd
     python -m venv venv
     venv\Scripts\activate.bat
     ```
   * En Linux / macOS:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```

---

## 📁 Estructura Modular del Proyecto

El proyecto sigue una arquitectura **MVC desacoplada** para Kivy, donde cada pantalla tiene su propio archivo de lógica en Python (`screens/`) y su diseño declarativo independiente en Kivy (`kv/`), coordinados por el núcleo central (`main.py`):

```text
proyecto_movil/
│
├── venv/                     # Entorno virtual local (ignorado por Git)
├── main.py                   # Núcleo de la App, ScreenManager, DataStore y estilos
├── requirements.txt          # Dependencias (kivy==2.3.0)
├── .gitignore                # Exclusiones de Git (venv/, __pycache__/)
├── README.md                 # Guía y documentación del proyecto
│
├── kv/                       # VISTAS DECLARATIVAS (.kv independientes)
│   ├── welcome.kv            # Pantalla de bienvenida y presentación
│   ├── home.kv               # Dashboard principal, resumen y accesos rápidos
│   ├── subjects.kv           # Listado de materias y porcentajes evaluados
│   ├── detail.kv             # Detalle de notas, categorías y cálculo predictivo
│   ├── schedule.kv           # Horario semanal interactivo y selector de días
│   ├── import_schedule.kv    # Asistente de importación de horario (4 pasos)
│   ├── calc.kv               # Calculadora académica ponderada y simulación libre
│   ├── progress.kv           # Gráficas de evolución, métricas y logros
│   ├── diary.kv              # Diario personal (preguntas guiadas e historial)
│   ├── remind.kv             # Configuración de recordatorios de clases y deberes
│   └── profile.kv            # Perfil del estudiante y ajustes globales
│
└── screens/                  # CONTROLADORES Y LÓGICA (.py independientes)
    ├── __init__.py           # Inicializador del paquete de pantallas
    ├── welcome_screen.py     # Lógica WelcomeScreen
    ├── home_screen.py        # Lógica HomeScreen y actualización de resumen
    ├── subjects_screen.py    # Lógica SubjectsScreen y selección de asignatura
    ├── detail_screen.py      # Lógica DetailScreen y modales de notas/categorías
    ├── schedule_screen.py    # Lógica ScheduleScreen y modal de edición de clase
    ├── import_screen.py      # Lógica ImportScreen y flujo paso a paso OCR
    ├── calc_screen.py        # Lógica CalcScreen y fórmulas de simulación
    ├── progress_screen.py    # Lógica ProgressScreen y modal de logros
    ├── diary_screen.py       # Lógica DiaryScreen y modal de edición de entradas
    ├── remind_screen.py      # Lógica RemindScreen y modal de configuración
    └── profile_screen.py     # Lógica ProfileScreen y preferencias
```

---

## 🧭 Navegación y Flujo de Pantallas

1. **Pila de Navegación (*History Stack*):**
   * `app.go_screen('nombre_pantalla')`: Transiciona a la pantalla y registra la anterior en la pila para soportar el botón `‹ Volver`.
   * `app.go_back()`: Extrae la última pantalla del historial y transiciona en dirección reversa.
   * `app.show_toast(mensaje)`: Despliega una alerta flotante temporal en la parte inferior.

2. **Barra de Navegación Inferior (*Bottom Navigation Bar*):**
   * Presente en todas las pantallas principales (`home`, `subjects`, `schedule`, `profile`).
   * Resalta automáticamente la pestaña activa correspondiente.

3. **Gestión de Estado Compartido (*DataStore*):**
   * Centralizado en `app.data_store` para que cualquier pantalla pueda consultar y actualizar calificaciones, clases, notas del diario y recordatorios sin acoplamientos circulares.

---

## 🤝 Colaboración en Git sin Conflictos

* **Regla 1:** Cada integrante trabaja exclusivamente en el par de archivos asignados (`screens/<pantalla>_screen.py` y `kv/<pantalla>.kv`).
* **Regla 2:** Toda interacción con otras pantallas o con el estado se realiza mediante los métodos públicos de `App.get_running_app()` (`go_screen`, `go_back`, `show_toast`, `data_store`).
* **Regla 3:** Crea ramas por funcionalidad (`feature/nombre-de-la-tarea`) y realiza un Pull Request antes de fusionar en `main`.
