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
        text: "👤\\nPerfil"
        halign: 'center'
        font_size: '11sp'
        background_normal: ''
        background_color: (0, 0, 0, 0)
        color: (0.545, 0.718, 1.0, 1) if app.active_tab == 'profile' else (0.627, 0.682, 0.753, 1)
        bold: app.active_tab == 'profile'
        on_release: app.go_screen('profile', clear_history=True)
"""


class DataStore:
    """Almacén central del estado académico de StudyMate"""
    def __init__(self):
        # Materias del semestre
        self.subjects = [
            {'n': 'Cálculo Diferencial', 'a': 8.4, 'p': 70},
            {'n': 'Programación II', 'a': 9.1, 'p': 85},
            {'n': 'Física General', 'ph': 1},
            {'n': 'Inglés Técnico', 'a': 9.5, 'p': 40}
        ]

        # Categorías y evaluaciones para la materia con seguimiento detallado
        self.categories = [
            {'n': 'Deberes', 'w': 20, 'm': 'a', 'it': [{'n': 'Deber 1', 'g': 8.5}, {'n': 'Deber 2', 'g': 9.0}, {'n': 'Deber 3', 'g': 7.5}]},
            {'n': 'Lecciones', 'w': 15, 'm': 'a', 'it': [{'n': 'Lección 1', 'g': 6.0}, {'n': 'Lección 2', 'g': 8.0}]},
            {'n': 'Proyecto', 'w': 20, 'm': 'a', 'it': [{'n': 'Proyecto final', 'g': 7.0}]},
            {'n': 'Examen final', 'w': 45, 'm': 'a', 'it': []}
        ]

        self.pmin = 7.0
        self.pgoal = 8.5
        self.teacher = 'Prof. Andrade'
        self.active_subject = 'Física General'

        # Horario semanal (0: Lunes a 4: Viernes)
        self.schedule = [
            [
                {'n': 'Cálculo Diferencial', 'h': '08:00 – 10:00', 'a': 'B-204'},
                {'n': 'Programación II', 'h': '10:30 – 12:30', 'a': 'Lab 3'},
                {'n': 'Física General', 'h': '14:00 – 16:00', 'a': 'A-110'}
            ],
            [
                {'n': 'Inglés Técnico', 'h': '09:00 – 11:00', 'a': 'C-301'},
                {'n': 'Programación II', 'h': '11:30 – 13:30', 'a': 'Lab 3'}
            ],
            [
                {'n': 'Cálculo Diferencial', 'h': '08:00 – 10:00', 'a': 'B-204'}
            ],
            [
                {'n': 'Física General', 'h': '08:00 – 10:00', 'a': 'A-110'}
            ],
            []
        ]

        # Recordatorios
        self.reminders = [
            {'t': 'Clase de Física General', 'd': 'Hoy · 14:00', 'on': 1, 'm': 30},
            {'t': 'Deber 4 de Programación II', 'd': 'Hoy · 20:00', 'on': 1, 'm': 60},
            {'t': 'Lección 3 de Física General', 'd': 'Mié 4 nov · 10:00', 'on': 1, 'm': 30},
            {'t': 'Examen parcial de Cálculo', 'd': 'Vie 6 nov · 08:00', 'on': 1, 'm': 1440},
            {'t': 'Entrega del proyecto de Inglés', 'd': 'Lun 9 nov · 23:59', 'on': 0, 'm': 60}
        ]

        # Diario de reflexión
        self.diary_entries = [
            {
                'd': '1 nov 2026',
                'v': [
                    'Un domingo tranquilo para repasar.',
                    'Cómo aplicar la regla de la cadena.',
                    'Mantener la atención en las tardes.',
                    'Estudiar en bloques de 25 minutos.',
                    'Terminé el repaso de Cálculo.'
                ]
            },
            {
                'd': '30 oct 2026',
                'v': [
                    'Día intenso, pero salió bien.',
                    'Estructuras de datos básicas.',
                    'El laboratorio de Programación.',
                    'Pedir ayuda antes.',
                    'Entregué el deber a tiempo.'
                ]
            }
        ]

        self.diary_questions = [
            '¿Cómo te fue hoy?',
            '¿Qué aprendiste?',
            '¿Qué te costó?',
            '¿Qué quieres mejorar?',
            '¿Cuál fue tu pequeño logro?'
        ]

        self.global_notifications = True

    def calc_categories(self):
        pts = 0.0
        ev = 0.0
        tot = 0.0
        for c in self.categories:
            if c.get('m') == 'a':
                tot += c.get('w', 0)
                graded = [it for it in c.get('it', []) if it.get('g') is not None]
                if graded:
                    avg = sum(it['g'] for it in graded) / len(graded)
                    pts += avg * c.get('w', 0) / 100.0
                    ev += c.get('w', 0)
            else:
                for it in c.get('it', []):
                    tot += it.get('w', 0)
                    if it.get('g') is not None:
                        pts += it['g'] * it.get('w', 0) / 100.0
                        ev += it.get('w', 0)
        return {'pts': pts, 'ev': ev, 'tot': tot, 'pend': tot - ev}

    def get_categories_avg(self):
        k = self.calc_categories()
        return (k['pts'] / k['ev'] * 100.0) if k['ev'] > 0 else 0.0

    def get_subject_avg(self, subj):
        if subj.get('ph'):
            return self.get_categories_avg()
        return subj.get('a', 0.0)

    def get_subject_progress(self, subj):
        if subj.get('ph'):
            return self.calc_categories()['ev']
        return subj.get('p', 0.0)

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
    'calc': 'home',
    'diary': 'home',
    'progress': 'home',
    'remind': 'home',
    'subjects': 'subjects',
    'detail': 'subjects',
    'schedule': 'schedule',
    'import_schedule': 'schedule',
    'profile': 'profile'
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
