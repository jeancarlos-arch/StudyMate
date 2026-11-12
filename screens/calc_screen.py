import ast
import operator as op
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.app import App


# Operadores seguros para la calculadora básica
SAFE_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.USub: op.neg,
    ast.UAdd: op.pos
}


def evaluate_arithmetic(expression_str):
    """Evalúa de forma segura expresiones matemáticas simples sin usar eval()."""
    cleaned = expression_str.replace('×', '*').replace('÷', '/').replace('−', '-').strip()
    if not cleaned:
        return 0

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type in SAFE_OPERATORS:
                if op_type is ast.Div and right == 0:
                    raise ZeroDivisionError("División por cero")
                return SAFE_OPERATORS[op_type](left, right)
            raise TypeError("Operador no soportado")
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in SAFE_OPERATORS:
                return SAFE_OPERATORS[op_type](_eval(node.operand))
            raise TypeError("Operador unario no soportado")
        else:
            raise TypeError("Sintaxis no permitida")

    tree = ast.parse(cleaned, mode='eval')
    return _eval(tree)


class CalcScreen(Screen):
    # Modo activo: 'weighted' (promedio académico) o 'standard' (calculadora básica)
    active_calc_mode = StringProperty('weighted')

    # Propiedades Calculadora Básica
    calc_expression = StringProperty("")
    calc_display = StringProperty("0")

    # Propiedades Calculadora Académica Ponderada
    scale_max = NumericProperty(10.0)
    scale_min = NumericProperty(7.0)
    scale_goal = NumericProperty(8.5)
    sim_grade_text = StringProperty("")

    evaluated_text = StringProperty("0%")
    pending_text = StringProperty("100%")
    current_avg_text = StringProperty("0.00")
    accum_pts_text = StringProperty("0.00 de 10.0")
    max_possible_text = StringProperty("10.00")
    goal_status_text = StringProperty("")
    min_status_text = StringProperty("")
    sim_result_text = StringProperty("")
    warning_text = StringProperty("")
    progress_percent = NumericProperty(0)
    status_badge_text = StringProperty("Sin notas")
    status_badge_color = ListProperty([0.545, 0.718, 1.0, 1])

    # Lista de notas académica
    grades_list = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_num = ""
        self._expr_chain = ""
        self._just_evaluated = False

    def on_pre_enter(self, *args):
        self.rebuild_grades_ui()
        self.calculate_results(silent=True)

    def set_mode(self, mode):
        self.active_calc_mode = mode

    # ---------------------------------------------------------
    # LÓGICA DE LA CALCULADORA BÁSICA (ARITMÉTICA)
    # ---------------------------------------------------------
    def on_key_press(self, key):
        if key == 'C':
            # Borrar todo
            self.calc_display = "0"
            self.calc_expression = ""
            self._current_num = ""
            self._expr_chain = ""
            self._just_evaluated = False

        elif key == 'DEL':
            # Retroceso de un caracter
            if self._just_evaluated:
                self.calc_expression = ""
                self._just_evaluated = False
            if self._current_num:
                self._current_num = self._current_num[:-1]
                self.calc_display = self._current_num if self._current_num else "0"

        elif key == 'NEG':
            # Cambiar signo ±
            target = self._current_num if self._current_num else self.calc_display
            if target and target != "0" and target != "Error":
                if target.startswith("-"):
                    target = target[1:]
                else:
                    target = "-" + target
                self._current_num = target
                self.calc_display = target

        elif key == '%':
            # Porcentaje del valor actual
            target = self._current_num if self._current_num else self.calc_display
            try:
                val = float(target) / 100.0
                formatted = f"{val:.6g}"
                self._current_num = formatted
                self.calc_display = formatted
            except ValueError:
                pass

        elif key in ['+', '−', '×', '÷']:
            if self._just_evaluated:
                self._expr_chain = f"{self.calc_display} {key} "
                self._current_num = ""
                self._just_evaluated = False
            elif self._current_num:
                self._expr_chain += f"{self._current_num} {key} "
                self._current_num = ""
            elif self._expr_chain:
                # Cambiar el último operador
                tokens = self._expr_chain.rstrip().split()
                if tokens and tokens[-1] in ['+', '−', '×', '÷']:
                    tokens[-1] = key
                    self._expr_chain = " ".join(tokens) + " "

            self.calc_expression = self._expr_chain
            self.calc_display = "0"

        elif key == '=':
            full_expr = self._expr_chain + (self._current_num if self._current_num else "")
            full_expr = full_expr.strip()
            if not full_expr:
                return

            try:
                res = evaluate_arithmetic(full_expr)
                if isinstance(res, float) and res.is_integer():
                    res_str = str(int(res))
                elif isinstance(res, float):
                    res_str = f"{res:.6g}"
                else:
                    res_str = str(res)

                self.calc_expression = f"{full_expr} ="
                self.calc_display = res_str
                self._current_num = res_str
                self._expr_chain = ""
                self._just_evaluated = True
            except ZeroDivisionError:
                self.calc_display = "Error: Div / 0"
                self._current_num = ""
                self._expr_chain = ""
                self._just_evaluated = True
            except Exception:
                self.calc_display = "Error"
                self._current_num = ""
                self._expr_chain = ""
                self._just_evaluated = True

        elif key == '.':
            if self._just_evaluated:
                self._current_num = "0."
                self._expr_chain = ""
                self._just_evaluated = False
            elif "." not in self._current_num:
                self._current_num = (self._current_num or "0") + "."
            self.calc_display = self._current_num

        else:
            # Dígitos 0-9
            if self._just_evaluated:
                self._current_num = key
                self._expr_chain = ""
                self._just_evaluated = False
            elif self._current_num == "0":
                self._current_num = key
            else:
                self._current_num += key
            self.calc_display = self._current_num

    # ---------------------------------------------------------
    # LÓGICA DE LA CALCULADORA ACADÉMICA PONDERADA
    # ---------------------------------------------------------
    def reset_example(self):
        self.scale_max = 10.0
        self.scale_min = 7.0
        self.scale_goal = 8.5
        self.sim_grade_text = ""
        self.grades_list = [
            {'n': 'Deberes y Talleres', 'g': 8.5, 'w': 25.0},
            {'n': 'Lecciones / Quizzes', 'g': 7.0, 'w': 25.0},
            {'n': 'Proyecto Final', 'g': 9.0, 'w': 20.0}
        ]
        self.rebuild_grades_ui()
        self.calculate_results(silent=True)

    def clear_all_grades(self):
        self.grades_list = []
        self.rebuild_grades_ui()
        self.calculate_results(silent=True)
        App.get_running_app().show_toast("Se vaciaron todas las notas")

    def distribute_weights_equally(self):
        """Distribuye el 100% equitativamente entre las notas existentes."""
        count = len(self.grades_list)
        if count == 0:
            App.get_running_app().show_toast("No hay notas para distribuir pesos")
            return

        base_w = round(100.0 / count, 1)
        rem = round(100.0 - (base_w * count), 1)

        for idx, item in enumerate(self.grades_list):
            item['w'] = base_w + (rem if idx == 0 else 0.0)

        self.rebuild_grades_ui()
        self.calculate_results(silent=True)
        App.get_running_app().show_toast("Pesos repartidos equitativamente (100%)")

    def load_from_subject(self):
        """Carga las materias o categorías configuradas en el DataStore."""
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        if not store.subjects:
            app.show_toast("No tienes materias registradas en 'Mis materias'")
            return

        new_list = []
        target_subj = store.get_active_subject_obj() or store.subjects[0]
        categories = target_subj.get('categories', [])

        if categories:
            for cat in categories:
                name = cat.get('n', 'Rubro')
                weight = float(cat.get('w', 0))
                items = cat.get('it', [])
                graded = [it for it in items if it.get('g') is not None]
                if graded:
                    avg = sum(float(it['g']) for it in graded) / len(graded)
                    new_list.append({'n': name, 'g': round(avg, 2), 'w': weight})
                else:
                    new_list.append({'n': name, 'g': 0.0, 'w': weight})
        else:
            for s in store.subjects:
                s_avg = store.get_subject_avg(s)
                new_list.append({'n': s.get('n', 'Materia'), 'g': round(s_avg, 2), 'w': 0.0})

        if new_list:
            self.grades_list = new_list
            self.rebuild_grades_ui()
            self.calculate_results(silent=True)
            app.show_toast(f"Cargadas {len(new_list)} evaluaciones")
        else:
            app.show_toast("No hay evaluaciones disponibles en las materias")

    def rebuild_grades_ui(self):
        container = self.ids.get('grades_container')
        if not container:
            return
        container.clear_widgets()

        if not self.grades_list:
            empty_box = BoxLayout(orientation='vertical', size_hint_y=None, height='90dp', padding=[14, 14], spacing=6)
            with empty_box.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.106, 0.149, 0.220, 0.6)
                r_c = RoundedRectangle(pos=empty_box.pos, size=empty_box.size, radius=[10])
                empty_box.bind(pos=lambda obj, val, r=r_c: setattr(r, 'pos', val),
                               size=lambda obj, val, r=r_c: setattr(r, 'size', val))

            lbl1 = Label(text="[b]No hay evaluaciones en la lista[/b]", markup=True,
                         color=(0.957, 0.965, 0.980, 1), font_size='14sp', size_hint_y=None, height='22dp')
            lbl2 = Label(text="Toca '➕ Agregar nota' o '📚 Cargar de materias' para comenzar.",
                         color=(0.627, 0.682, 0.753, 1), font_size='12sp', size_hint_y=None, height='20dp')
            empty_box.add_widget(lbl1)
            empty_box.add_widget(lbl2)
            container.add_widget(empty_box)
            return

        for idx, item in enumerate(self.grades_list):
            card = BoxLayout(orientation='vertical', size_hint_y=None, height='100dp', padding=[14, 10], spacing=6)
            with card.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.106, 0.149, 0.220, 1)
                r_c = RoundedRectangle(pos=card.pos, size=card.size, radius=[10])
                card.bind(pos=lambda obj, val, r=r_c: setattr(r, 'pos', val),
                          size=lambda obj, val, r=r_c: setattr(r, 'size', val))

            # Fila Superior: Nombre de evaluación y botón de eliminar
            top_row = BoxLayout(size_hint_y=None, height='32dp', spacing=8)

            txt_name = TextInput(
                text=str(item.get('n', f'Nota {idx + 1}')),
                multiline=False,
                size_hint_y=None,
                height='32dp',
                background_normal='',
                background_active='',
                background_color=(0.063, 0.094, 0.153, 1),
                foreground_color=(0.957, 0.965, 0.980, 1),
                cursor_color=(0.545, 0.718, 1.0, 1),
                padding=[8, 6],
                font_size='13sp'
            )
            txt_name.bind(text=lambda inst, val, i=idx: self.update_grade_val(i, 'n', val, is_str=True))

            btn_del = Button(
                text="🗑 Eliminar",
                size_hint=(None, None),
                size=('84dp', '30dp'),
                background_normal='',
                background_color=(0.173, 0.227, 0.322, 0.5),
                color=(0.949, 0.651, 0.353, 1),
                font_size='12sp'
            )
            btn_del.bind(on_release=lambda x, i=idx: self.remove_grade(i))

            top_row.add_widget(txt_name)
            top_row.add_widget(btn_del)

            # Fila Inferior: Inputs numéricos de Nota y Peso %
            inputs_row = BoxLayout(size_hint_y=None, height='36dp', spacing=12)

            # Bloque Nota
            b_g = BoxLayout(orientation='horizontal', spacing=6)
            b_g.add_widget(Label(text="Nota:", color=(0.627, 0.682, 0.753, 1), font_size='12sp', size_hint_x=None, width='40dp'))
            txt_g = TextInput(
                text=str(item.get('g', 0.0)),
                multiline=False,
                input_filter='float',
                size_hint_y=None,
                height='34dp',
                background_normal='',
                background_active='',
                background_color=(0.063, 0.094, 0.153, 1),
                foreground_color=(0.957, 0.965, 0.980, 1),
                cursor_color=(0.545, 0.718, 1.0, 1),
                padding=[8, 6],
                font_size='13sp'
            )
            txt_g.bind(text=lambda inst, val, i=idx: self.update_grade_val(i, 'g', val))
            b_g.add_widget(txt_g)

            # Bloque Peso %
            b_w = BoxLayout(orientation='horizontal', spacing=6)
            b_w.add_widget(Label(text="Peso %:", color=(0.627, 0.682, 0.753, 1), font_size='12sp', size_hint_x=None, width='50dp'))
            txt_w = TextInput(
                text=str(item.get('w', 0.0)),
                multiline=False,
                input_filter='float',
                size_hint_y=None,
                height='34dp',
                background_normal='',
                background_active='',
                background_color=(0.063, 0.094, 0.153, 1),
                foreground_color=(0.957, 0.965, 0.980, 1),
                cursor_color=(0.545, 0.718, 1.0, 1),
                padding=[8, 6],
                font_size='13sp'
            )
            txt_w.bind(text=lambda inst, val, i=idx: self.update_grade_val(i, 'w', val))
            b_w.add_widget(txt_w)

            inputs_row.add_widget(b_g)
            inputs_row.add_widget(b_w)

            card.add_widget(top_row)
            card.add_widget(inputs_row)
            container.add_widget(card)

    def update_grade_val(self, index, field, val_text, is_str=False):
        if index < len(self.grades_list):
            if is_str:
                self.grades_list[index][field] = val_text
            else:
                try:
                    val = float(val_text) if val_text else 0.0
                    self.grades_list[index][field] = max(0.0, val)
                except ValueError:
                    pass
            self.calculate_results(silent=True)

    def add_grade(self):
        new_name = f"Evaluación {len(self.grades_list) + 1}"
        self.grades_list.append({'n': new_name, 'g': 0.0, 'w': 20.0})
        self.rebuild_grades_ui()
        self.calculate_results(silent=True)

    def remove_grade(self, index):
        if index < len(self.grades_list):
            self.grades_list.pop(index)
            self.rebuild_grades_ui()
            self.calculate_results(silent=True)

    def calculate_results(self, silent=False):
        sc = self.scale_max if self.scale_max > 0 else 10.0
        ev = sum(x.get('w', 0.0) for x in self.grades_list)
        pts = sum(x.get('g', 0.0) * x.get('w', 0.0) / 100.0 for x in self.grades_list)
        pe = max(0.0, round(100.0 - ev, 2))
        av = (pts / ev * 100.0) if ev > 0 else 0.0
        mx = pts + (sc * pe / 100.0)

        self.progress_percent = int(min(100, max(0, ev)))

        if ev > 100.0:
            self.warning_text = f"⚠️ La suma de pesos es {ev:.1f}%. Excede el 100% permitido."
            self.evaluated_text = f"{ev:.1f}%"
            self.pending_text = "0%"
            self.status_badge_text = "Exceso de peso %"
            self.status_badge_color = [0.949, 0.651, 0.353, 1]
            return
        else:
            self.warning_text = ""

        self.evaluated_text = f"{ev:.1f}%"
        self.pending_text = f"{pe:.1f}%"
        self.current_avg_text = f"{av:.2f}"
        self.accum_pts_text = f"{pts:.2f} de {sc:.1f}"
        self.max_possible_text = f"{mx:.2f}"

        # Estado badge
        if av >= self.scale_min:
            self.status_badge_text = "En curso · Aprobando"
            self.status_badge_color = [0.224, 0.788, 0.541, 1]
        elif ev > 0:
            self.status_badge_text = "En curso · Atención requerida"
            self.status_badge_color = [0.949, 0.651, 0.353, 1]
        else:
            self.status_badge_text = "Sin evaluaciones"
            self.status_badge_color = [0.627, 0.682, 0.753, 1]

        app = App.get_running_app()
        if app and hasattr(app, 'data_store'):
            store = app.data_store
            _, g_msg = store.calc_need(self.scale_goal, pts, pe, sc)
            _, m_msg = store.calc_need(self.scale_min, pts, pe, sc)
            self.goal_status_text = f"Objetivo ({self.scale_goal:.1f}): {g_msg}"
            self.min_status_text = f"Aprobación ({self.scale_min:.1f}): {m_msg}"

        sim_input = self.sim_grade_text.strip()
        if sim_input and pe > 0:
            try:
                sim_val = float(sim_input)
                fn = pts + (sim_val * pe / 100.0)
                status_str = "Aprobado 🎉" if fn >= self.scale_min else "Por debajo del mínimo ⚠️"
                self.sim_result_text = f"Simulación: obteniendo {sim_val:.2f} en el {pe:.0f}% pendiente, tu nota final sería {fn:.2f} ({status_str})."
            except ValueError:
                self.sim_result_text = ""
        else:
            self.sim_result_text = ""

        if not silent and app:
            app.show_toast("Resultados actualizados")
