from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.app import App


class SubjectCard(Button):
    def __init__(self, subject_data, on_select_cb, **kwargs):
        super().__init__(**kwargs)
        self.subject_data = subject_data
        self.on_select_cb = on_select_cb
        self.size_hint_y = None
        self.height = '88dp'
        self.background_normal = ''
        self.background_color = (0.106, 0.149, 0.220, 1)  # --sf


class SubjectsScreen(Screen):
    subtitle_text = StringProperty("4 materias este semestre")

    def on_pre_enter(self, *args):
        self.refresh_subjects()

    def refresh_subjects(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        subjects = store.subjects
        self.subtitle_text = f"{len(subjects)} materias este semestre"

        container = self.ids.get('subjects_container')
        if not container:
            return

        container.clear_widgets()
        for subj in subjects:
            name = subj.get('n', 'Materia')
            avg = store.get_subject_avg(subj)
            evaluated = store.get_subject_progress(subj)

            card = BoxLayout(orientation='vertical', size_hint_y=None, height='94dp', padding=[14, 12], spacing=6)
            
            # Canvas de fondo
            with card.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.106, 0.149, 0.220, 1)
                rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
                card.bind(pos=lambda obj, val, r=rect: setattr(r, 'pos', val),
                          size=lambda obj, val, r=rect: setattr(r, 'size', val))

            # Fila superior: Nombre y Nota
            top_row = BoxLayout(size_hint_y=None, height='28dp')
            lbl_name = Label(text=f"[b]{name}[/b]", markup=True, halign='left', valign='middle',
                             color=(0.957, 0.965, 0.980, 1), font_size='15sp')
            lbl_name.bind(size=lbl_name.setter('text_size'))

            color_grade = (0.224, 0.788, 0.541, 1) if avg >= 7.0 else (0.949, 0.651, 0.353, 1)
            lbl_grade = Label(text=f"[b]{avg:.2f}[/b]", markup=True, halign='right', valign='middle',
                              color=color_grade, font_size='18sp', size_hint_x=None, width='70dp')
            lbl_grade.bind(size=lbl_grade.setter('text_size'))
            top_row.add_widget(lbl_name)
            top_row.add_widget(lbl_grade)

            # Subtítulo: Evaluado
            lbl_sub = Label(text=f"Promedio actual · {evaluated:.0f}% evaluado", halign='left', valign='middle',
                            color=(0.627, 0.682, 0.753, 1), font_size='12sp', size_hint_y=None, height='18dp')
            lbl_sub.bind(size=lbl_sub.setter('text_size'))

            # Barra de progreso
            from kivy.uix.widget import Widget
            bar = Widget(size_hint_y=None, height='6dp')
            with bar.canvas:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.063, 0.094, 0.153, 1)
                r_bg = RoundedRectangle(pos=bar.pos, size=bar.size, radius=[3])
                Color(*color_grade)
                r_fill = RoundedRectangle(pos=bar.pos, size=(bar.width * (min(100, evaluated) / 100.0), bar.height), radius=[3])

                def update_bar(w, val, r_b=r_bg, r_f=r_fill, ev=evaluated):
                    r_b.pos = w.pos
                    r_b.size = w.size
                    r_f.pos = w.pos
                    r_f.size = (w.width * (min(100, ev) / 100.0), w.height)

                bar.bind(pos=update_bar, size=update_bar)

            card.add_widget(top_row)
            card.add_widget(lbl_sub)
            card.add_widget(bar)

            # Botón transparente encima para capturar click
            btn_wrapper = Button(background_color=(0,0,0,0), size_hint=(1, 1))
            btn_wrapper.bind(on_release=lambda instance, s=subj: self.open_detail(s))
            
            # Para hacer clickeable la tarjeta:
            container_card = BoxLayout(size_hint_y=None, height='94dp')
            from kivy.uix.relativelayout import RelativeLayout
            rl = RelativeLayout(size_hint_y=None, height='94dp')
            rl.add_widget(card)
            rl.add_widget(btn_wrapper)
            container.add_widget(rl)

    def open_detail(self, subject):
        app = App.get_running_app()
        app.data_store.active_subject = subject.get('n', 'Física General')
        app.go_screen('detail')

    def add_subject_prompt(self):
        app = App.get_running_app()
        app.show_toast("Función para agregar materia")
