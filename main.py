import os
import sys
from kivy.config import Config

# Configuración de ventana para apariencia móvil en desarrollo de escritorio
Config.set('graphics', 'width', '390')
Config.set('graphics', 'height', '780')
Config.set('graphics', 'resizable', '1')

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.clock import Clock

# Definir color de fondo global (--bg: #101827)
Window.clearcolor = (0.063, 0.094, 0.153, 1)

# Importar las clases de pantallas
from screens.welcome_screen import WelcomeScreen
from screens.home_screen import HomeScreen
from screens.subjects_screen import SubjectsScreen
from screens.detail_screen import DetailScreen
from screens.schedule_screen import ScheduleScreen
from screens.import_screen import ImportScreen
from screens.calc_screen import CalcScreen
from screens.progress_screen import ProgressScreen
from screens.diary_screen import DiaryScreen
from screens.remind_screen import RemindScreen
from screens.profile_screen import ProfileScreen
from screens.login_screen import LoginScreen


# Componentes y estilos globales en KV
GLOBAL_KV = """
#:import dp kivy.metrics.dp

<DarkCard@BoxLayout>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: dp(14)
    spacing: dp(8)
    canvas.before:
        Color:
            rgba: (0.106, 0.149, 0.220, 1) # --sf
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]

<PrimaryButton@Button>:
    size_hint_y: None
    height: dp(46)
    background_normal: ''
    background_color: (0.337, 0.537, 0.910, 1) # --bl
    color: (0.063, 0.094, 0.153, 1) # --bg
    bold: True
    font_size: '15sp'

<GhostButton@Button>:
    size_hint_y: None
    height: dp(44)
    background_normal: ''
    background_color: (0.106, 0.149, 0.220, 1) # --sf
    color: (0.545, 0.718, 1.0, 1) # --bl2
    bold: True
    font_size: '14sp'

<DangerButton@Button>:
    size_hint_y: None
    height: dp(42)
    background_normal: ''
    background_color: (0.106, 0.149, 0.220, 1)
    color: (0.949, 0.651, 0.353, 1)
    font_size: '13sp'

<StyledTextInput@TextInput>:
    size_hint_y: None
    height: dp(40)
    multiline: False
    background_normal: ''
    background_active: ''
    background_color: (0.063, 0.094, 0.153, 1)
    foreground_color: (0.957, 0.965, 0.980, 1)
    cursor_color: (0.545, 0.718, 1.0, 1)
    hint_text_color: (0.627, 0.682, 0.753, 0.6)
    padding: [dp(10), dp(8)]

<CustomProgressBar@Widget>:
    value: 0
    bar_color: (0.224, 0.788, 0.541, 1)
    size_hint_y: None
    height: dp(7)
    canvas:
        Color:
            rgba: (0.063, 0.094, 0.153, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(4)]
        Color:
            rgba: self.bar_color
        RoundedRectangle:
            pos: self.pos
            size: (self.width * min(1.0, max(0.0, self.value / 100.0)), self.height)
            radius: [dp(4)]

<TileButton@Button>:
    icon_text: ""
    title_text: ""
    text: f"{self.icon_text}\\n{self.title_text}"
    halign: 'center'
    valign: 'middle'
    font_size: '13sp'
    background_normal: ''
    background_color: (0.106, 0.149, 0.220, 1)
    color: (0.545, 0.718, 1.0, 1)
    bold: True

<ProfileLinkCard@Button>:
    icon_text: ""
    link_title: ""
    text: f"  {self.icon_text}   {self.link_title}"
    halign: 'left'
    font_size: '14sp'
    size_hint_y: None
    height: dp(50)
    background_normal: ''
    background_color: (0.106, 0.149, 0.220, 1)
    color: (0.957, 0.965, 0.980, 1)

<NavBar@BoxLayout>:
    size_hint_y: None
    height: dp(62)
    padding: [dp(6), dp(4)]
    spacing: dp(4)
    canvas.before:
        Color:
            rgba: (0.106, 0.149, 0.220, 1) # --sf
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: (0.173, 0.227, 0.322, 1) # --ln
        Line:
            points: [self.x, self.top, self.right, self.top]
            width: dp(1)

    Button:
        text: "🏠\\nInicio"
        halign: 'center'
        font_size: '11sp'
        background_normal: ''
        background_color: (0, 0, 0, 0)
        color: (0.545, 0.718, 1.0, 1) if app.active_tab == 'home' else (0.627, 0.682, 0.753, 1)
        bold: app.active_tab == 'home'
        on_release: app.go_screen('home', clear_history=True)

    Button:
        text: "📚\\nMaterias"
        halign: 'center'
        font_size: '11sp'
        background_normal: ''
        background_color: (0, 0, 0, 0)
        color: (0.545, 0.718, 1.0, 1) if app.active_tab == 'subjects' else (0.627, 0.682, 0.753, 1)
        bold: app.active_tab == 'subjects'
        on_release: app.go_screen('subjects', clear_history=True)

    Button:
        text: "📅\\nHorario"
        halign: 'center'
        font_size: '11sp'
        background_normal: ''
        background_color: (0, 0, 0, 0)
        color: (0.545, 0.718, 1.0, 1) if app.active_tab == 'schedule' else (0.627, 0.682, 0.753, 1)
        bold: app.active_tab == 'schedule'
        on_release: app.go_screen('schedule', clear_history=True)

    Button:
        text: "🔢\\nCalculadora"
        halign: 'center'
        font_size: '11sp'
        background_normal: ''
        background_color: (0, 0, 0, 0)
        color: (0.545, 0.718, 1.0, 1) if app.active_tab == 'calc' else (0.627, 0.682, 0.753, 1)
        bold: app.active_tab == 'calc'
        on_release: app.go_screen('calc', clear_history=True)
"""


class DataStore:
    """Almacén central del estado académico de StudyMate"""
    def __init__(self):
        # Datos del perfil del estudiante
        self.student_name = ""
        self.student_career = ""
        self.student_semester = ""
        self.is_logged_in = False

        # Materias del semestre (inicia vacío sin datos quemados)
        self.subjects = []

        # Horario semanal (0: Lunes a 4: Viernes) -> Inicia vacío
        self.schedule = [[], [], [], [], []]

        # Materia activa seleccionada para detalle
        self.active_subject = ""

        # Notificaciones y configuraciones
        self.global_notifications = True
        self.reminders = []
        self.diary_entries = []

    def get_active_subject_obj(self):
        for s in self.subjects:
            if s.get('n') == self.active_subject:
                return s
        return None

    def calc_categories_for(self, cat_list):
        pts = 0.0
        ev = 0.0
        tot = 0.0
        for c in cat_list:
            w = float(c.get('w', 0))
            tot += w
            graded = [it for it in c.get('it', []) if it.get('g') is not None]
            if graded:
                avg = sum(float(it['g']) for it in graded) / len(graded)
                pts += avg * w / 100.0
                ev += w
        return {'pts': pts, 'ev': ev, 'tot': tot, 'pend': max(0.0, 100.0 - ev)}

    def get_subject_avg(self, subj):
        cats = subj.get('categories', [])
        if cats:
            k = self.calc_categories_for(cats)
            return (k['pts'] / k['ev'] * 100.0) if k['ev'] > 0 else 0.0
        return float(subj.get('a', 0.0))

    def get_subject_progress(self, subj):
        cats = subj.get('categories', [])
        if cats:
            return self.calc_categories_for(cats)['ev']
        return float(subj.get('p', 0.0))

    def get_general_avg(self):
        if not self.subjects:
            return 0.0
        return sum(self.get_subject_avg(s) for s in self.subjects) / len(self.subjects)

    def get_general_adv(self):
        if not self.subjects:
            return 0.0
        return sum(self.get_subject_progress(s) for s in self.subjects) / len(self.subjects)

    def calc_need(self, goal, pts, pend, max_score=10.0):
        if pend <= 0:
            if pts >= goal:
                return ('ok', 'Meta alcanzada con tu nota final')
            return ('wa', 'No quedan evaluaciones y la meta no se alcanzó')

        n = (goal - pts) / (pend / 100.0)
        if n > max_score:
            return ('wa', f'Meta no alcanzable: necesitarías {n:.2f} y el máximo es {max_score:.1f}')
        if n <= 0:
            return ('ok', '¡Meta asegurada! Ya la alcanzaste')
        return ('ok', f'Necesitas {n:.2f} en el {pend:.0f}% pendiente')


TAB_MAP = {
    'home': 'home',
    'calc': 'calc',
    'diary': 'home',
    'progress': 'home',
    'remind': 'home',
    'subjects': 'subjects',
    'detail': 'subjects',
    'schedule': 'schedule',
    'import_schedule': 'schedule',
    'profile': 'home',
    'login': 'home'
}


class StudyMateApp(App):
    active_tab = StringProperty('home')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_store = DataStore()
        self.history_stack = []

    def build(self):
        self.title = "StudyMate"

        # Cargar estilos globales
        Builder.load_string(GLOBAL_KV)

        # Cargar los 11 archivos .kv modulares
        base_dir = os.path.dirname(os.path.abspath(__file__))
        kv_dir = os.path.join(base_dir, 'kv')
        kv_files = [
            'welcome.kv',
            'login.kv',
            'home.kv',
            'subjects.kv',
            'detail.kv',
            'schedule.kv',
            'import_schedule.kv',
            'calc.kv',
            'progress.kv',
            'diary.kv',
            'remind.kv',
            'profile.kv'
        ]

        for kv in kv_files:
            file_path = os.path.join(kv_dir, kv)
            if os.path.exists(file_path):
                Builder.load_file(file_path)

        # Contenedor raíz con ScreenManager y Toast flotante
        self.root_layout = FloatLayout()

        self.sm = ScreenManager(transition=SlideTransition())
        self.sm.add_widget(WelcomeScreen(name='welcome'))
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(SubjectsScreen(name='subjects'))
        self.sm.add_widget(DetailScreen(name='detail'))
        self.sm.add_widget(ScheduleScreen(name='schedule'))
        self.sm.add_widget(ImportScreen(name='import_schedule'))
        self.sm.add_widget(CalcScreen(name='calc'))
        self.sm.add_widget(ProgressScreen(name='progress'))
        self.sm.add_widget(DiaryScreen(name='diary'))
        self.sm.add_widget(RemindScreen(name='remind'))
        self.sm.add_widget(ProfileScreen(name='profile'))

        self.root_layout.add_widget(self.sm)

        # Widget Toast para mensajes emergentes
        self.toast_label = Label(
            text="",
            size_hint=(0.85, None),
            height='44dp',
            pos_hint={'center_x': 0.5, 'y': 0.11},
            color=(0.063, 0.094, 0.153, 1),
            font_size='13sp',
            bold=True,
            opacity=0
        )
        with self.toast_label.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            self.toast_color = Color(0.224, 0.788, 0.541, 0)
            self.toast_rect = RoundedRectangle(pos=self.toast_label.pos, size=self.toast_label.size, radius=[12])
            self.toast_label.bind(
                pos=lambda obj, val: setattr(self.toast_rect, 'pos', val),
                size=lambda obj, val: setattr(self.toast_rect, 'size', val)
            )

        self.root_layout.add_widget(self.toast_label)
        return self.root_layout

    def go_screen(self, screen_name, clear_history=False, direction='left'):
        if clear_history:
            self.history_stack.clear()
        elif self.sm.current != screen_name and self.sm.current != 'welcome':
            self.history_stack.append(self.sm.current)

        self.active_tab = TAB_MAP.get(screen_name, 'home')
        self.sm.transition.direction = direction
        self.sm.current = screen_name

    def go_back(self, direction='right'):
        if self.history_stack:
            prev = self.history_stack.pop()
            self.active_tab = TAB_MAP.get(prev, 'home')
            self.sm.transition.direction = direction
            self.sm.current = prev
        else:
            self.go_screen('home', clear_history=True, direction=direction)

    def show_toast(self, message):
        self.toast_label.text = message
        self.toast_label.opacity = 1
        self.toast_color.a = 1
        Clock.unschedule(self._hide_toast)
        Clock.schedule_once(self._hide_toast, 1.8)

    def _hide_toast(self, dt):
        self.toast_label.opacity = 0
        self.toast_color.a = 0


if __name__ == '__main__':
    StudyMateApp().run()
