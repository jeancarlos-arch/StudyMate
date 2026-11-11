from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App


class AchievementsModal(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.65)
        self.auto_dismiss = True

        root = BoxLayout(orientation='vertical', padding=16, spacing=10)
        with root.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.106, 0.149, 0.220, 1)
            rect = RoundedRectangle(pos=root.pos, size=root.size, radius=[16])
            root.bind(pos=lambda obj, val: setattr(rect, 'pos', val),
                      size=lambda obj, val: setattr(rect, 'size', val))

        root.add_widget(Label(text="[b]Tus logros[/b]", markup=True, font_size='18sp', size_hint_y=None, height='32dp'))

        achievements = [
            ("Primer 9 en Programación II", True),
            ("5 semanas de constancia", True),
            ("Meta alcanzada en Inglés Técnico", True),
            ("Primera entrada en tu diario", True),
            ("Promedio general de 9.0 (¡Estás muy cerca!)", False)
        ]

        for text, completed in achievements:
            row = BoxLayout(size_hint_y=None, height='44dp', padding=[10, 8])
            with row.canvas.before:
                from kivy.graphics import Color as RColor, RoundedRectangle as RRect
                RColor(0.063, 0.094, 0.153, 1)
                r_r = RRect(pos=row.pos, size=row.size, radius=[8])
                row.bind(pos=lambda obj, val, r=r_r: setattr(r, 'pos', val),
                         size=lambda obj, val, r=r_r: setattr(r, 'size', val))

            star_color = "39c98a" if completed else "a0aec0"
            star_symbol = "★" if completed else "☆"
            lbl = Label(text=f"[color={star_color}]{star_symbol}[/color]  {text}", markup=True,
                        font_size='13sp', halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            row.add_widget(lbl)
            root.add_widget(row)

        btn_close = Button(text="Cerrar", size_hint_y=None, height='42dp', background_normal='',
                           background_color=(0.106, 0.149, 0.220, 1), color=(0.545, 0.718, 1.0, 1))
        btn_close.bind(on_release=self.dismiss)
        root.add_widget(btn_close)

        self.add_widget(root)


class ProgressScreen(Screen):
    general_avg_text = StringProperty("8.76")
    semester_adv_text = StringProperty("70%")
    goals_met_text = StringProperty("3 de 4")
    best_subject_name = StringProperty("Inglés Técnico")
    best_subject_score = StringProperty("9.50")
    focus_subject_name = StringProperty("Física General")
    focus_subject_score = StringProperty("8.05")

    # Alturas para el gráfico de barras (en porcentaje o dp)
    p1_height = NumericProperty(78)
    p2_height = NumericProperty(82)
    current_height = NumericProperty(88)

    def on_pre_enter(self, *args):
        self.refresh_stats()

    def refresh_stats(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        avg = store.get_general_avg()
        adv = store.get_general_adv()

        self.general_avg_text = f"{avg:.2f}"
        self.semester_adv_text = f"{adv:.0f}%"
        self.current_height = min(100, int(avg * 10))

        # Materias mejor y a mejorar
        subjects = store.subjects
        sorted_subjs = sorted(subjects, key=lambda s: store.get_subject_avg(s), reverse=True)
        if sorted_subjs:
            best = sorted_subjs[0]
            worst = sorted_subjs[-1]
            self.best_subject_name = best.get('n', '')
            self.best_subject_score = f"{store.get_subject_avg(best):.2f}"
            self.focus_subject_name = worst.get('n', '')
            self.focus_subject_score = f"{store.get_subject_avg(worst):.2f}"

    def show_achievements(self):
        modal = AchievementsModal()
        modal.open()
