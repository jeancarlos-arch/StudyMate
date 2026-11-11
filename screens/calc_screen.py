from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App


class CalcScreen(Screen):
    scale_max = NumericProperty(10.0)
    scale_min = NumericProperty(7.0)
    scale_goal = NumericProperty(8.5)
    sim_grade_text = StringProperty("")
    
    evaluated_text = StringProperty("70%")
    pending_text = StringProperty("30%")
    current_avg_text = StringProperty("8.14")
    accum_pts_text = StringProperty("5.70 de 10")
    max_possible_text = StringProperty("8.70")
    goal_status_text = StringProperty("")
    min_status_text = StringProperty("")
    sim_result_text = StringProperty("")
    warning_text = StringProperty("")

    # Lista local de notas: [{'n': 'Nota 1', 'g': 8.0, 'w': 25}, ...]
    grades_list = []

    def on_pre_enter(self, *args):
        if not self.grades_list:
            self.reset_example()
        else:
            self.rebuild_grades_ui()
            self.calculate_results()

    def reset_example(self):
        self.scale_max = 10.0
        self.scale_min = 7.0
        self.scale_goal = 8.5
        self.sim_grade_text = ""
        self.grades_list = [
            {'n': 'Nota 1', 'g': 8.0, 'w': 25},
            {'n': 'Nota 2', 'g': 7.5, 'w': 25},
            {'n': 'Nota 3', 'g': 9.0, 'w': 20}
        ]
        self.rebuild_grades_ui()
        self.calculate_results()

    def rebuild_grades_ui(self):
        container = self.ids.get('grades_container')
        if not container:
            return
        container.clear_widgets()

        for idx, item in enumerate(self.grades_list):
            card = BoxLayout(orientation='vertical', size_hint_y=None, height='90dp', padding=[12, 8], spacing=6)
            with card.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.106, 0.149, 0.220, 1)
                r_c = RoundedRectangle(pos=card.pos, size=card.size, radius=[10])
                card.bind(pos=lambda obj, val, r=r_c: setattr(r, 'pos', val),
                          size=lambda obj, val, r=r_c: setattr(r, 'size', val))

            # Fila Título y botón eliminar
            top_row = BoxLayout(size_hint_y=None, height='24dp')
            lbl_title = Label(text=f"[b]{item.get('n', '')}[/b]", markup=True, halign='left',
                              color=(0.957, 0.965, 0.980, 1), font_size='14sp')
            lbl_title.bind(size=lbl_title.setter('text_size'))
            
            btn_del = Button(text="🗑 Eliminar", size_hint_x=None, width='90dp', background_normal='',
                             background_color=(0.106, 0.149, 0.220, 1), color=(0.949, 0.651, 0.353, 1),
                             font_size='12sp')
            btn_del.bind(on_release=lambda x, i=idx: self.remove_grade(i))
            top_row.add_widget(lbl_title)
            top_row.add_widget(btn_del)

            # Fila Inputs (Nota y Peso)
            inputs_row = BoxLayout(size_hint_y=None, height='38dp', spacing=10)
            
            b_g = BoxLayout(orientation='horizontal', spacing=4)
            b_g.add_widget(Label(text="Nota:", color=(0.627, 0.682, 0.753, 1), font_size='12sp', size_hint_x=None, width='40dp'))
            txt_g = TextInput(text=str(item.get('g', 0.0)), multiline=False, input_filter='float')
            txt_g.bind(text=lambda inst, val, i=idx: self.update_grade_val(i, 'g', val))
            b_g.add_widget(txt_g)

            b_w = BoxLayout(orientation='horizontal', spacing=4)
            b_w.add_widget(Label(text="Peso %:", color=(0.627, 0.682, 0.753, 1), font_size='12sp', size_hint_x=None, width='50dp'))
            txt_w = TextInput(text=str(item.get('w', 0)), multiline=False, input_filter='int')
            txt_w.bind(text=lambda inst, val, i=idx: self.update_grade_val(i, 'w', val))
            b_w.add_widget(txt_w)

            inputs_row.add_widget(b_g)
            inputs_row.add_widget(b_w)

            card.add_widget(top_row)
            card.add_widget(inputs_row)
            container.add_widget(card)

    def update_grade_val(self, index, field, val_text):
        try:
            val = float(val_text) if val_text else 0.0
            if index < len(self.grades_list):
                self.grades_list[index][field] = val
        except ValueError:
            pass

    def add_grade(self):
        new_name = f"Nota {len(self.grades_list) + 1}"
        self.grades_list.append({'n': new_name, 'g': 0.0, 'w': 0})
        self.rebuild_grades_ui()
        self.calculate_results()

    def remove_grade(self, index):
        if index < len(self.grades_list):
            self.grades_list.pop(index)
            self.rebuild_grades_ui()
            self.calculate_results()

    def calculate_results(self):
        sc = self.scale_max
        pts = sum(x.get('g', 0) * x.get('w', 0) / 100.0 for x in self.grades_list)
        ev = sum(x.get('w', 0) for x in self.grades_list)
        pe = max(0.0, round(100.0 - ev, 2))
        av = (pts / ev * 100.0) if ev > 0 else 0.0
        mx = pts + (sc * pe / 100.0)

        if ev > 100:
            self.warning_text = f"Los pesos suman {ev:.0f}%. Ajusta para que no superen 100%."
            self.evaluated_text = f"{ev:.0f}%"
            self.pending_text = "0%"
            return
        else:
            self.warning_text = ""

        self.evaluated_text = f"{ev:.0f}%"
        self.pending_text = f"{pe:.0f}%"
        self.current_avg_text = f"{av:.2f}"
        self.accum_pts_text = f"{pts:.2f} de {sc:.1f}"
        self.max_possible_text = f"{mx:.2f}"

        store = App.get_running_app().data_store
        _, g_msg = store.calc_need(self.scale_goal, pts, pe, sc)
        _, m_msg = store.calc_need(self.scale_min, pts, pe, sc)
        self.goal_status_text = f"Objetivo {self.scale_goal}: {g_msg}"
        self.min_status_text = f"Aprobar con {self.scale_min}: {m_msg}"

        sim_input = self.sim_grade_text.strip()
        if sim_input and pe > 0:
            try:
                sim_val = float(sim_input)
                fn = pts + (sim_val * pe / 100.0)
                status_str = "aprobado" if fn >= self.scale_min else "por debajo del mínimo"
                self.sim_result_text = f"Simulación: con {sim_val} en lo pendiente, tu nota final sería {fn:.2f} ({status_str}). No se guarda."
            except ValueError:
                self.sim_result_text = ""
        else:
            self.sim_result_text = ""

        App.get_running_app().show_toast("Resultados calculados")
