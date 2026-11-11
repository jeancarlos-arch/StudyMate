from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.uix.spinner import Spinner
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App


class EvaluationModal(ModalView):
    def __init__(self, category_index, item_index, on_save_cb, on_delete_cb=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.7)
        self.auto_dismiss = True
        self.background_color = (0, 0, 0, 0.7)
        
        app = App.get_running_app()
        store = app.data_store
        self.categories = store.categories
        self.cat_idx = category_index
        self.item_idx = item_index
        self.on_save_cb = on_save_cb
        self.on_delete_cb = on_delete_cb

        item_data = {}
        if item_index >= 0 and category_index < len(self.categories):
            items = self.categories[category_index].get('it', [])
            if item_index < len(items):
                item_data = items[item_index]

        root = BoxLayout(orientation='vertical', padding=16, spacing=10)
        with root.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.106, 0.149, 0.220, 1)
            rect = RoundedRectangle(pos=root.pos, size=root.size, radius=[16])
            root.bind(pos=lambda obj, val: setattr(rect, 'pos', val),
                      size=lambda obj, val: setattr(rect, 'size', val))

        title_text = "Editar evaluación" if item_index >= 0 else "Registrar evaluación"
        root.add_widget(Label(text=f"[b]{title_text}[/b]", markup=True, font_size='18sp', size_hint_y=None, height='32dp'))

        # Selector de Categoría
        root.add_widget(Label(text="Categoría", size_hint_y=None, height='20dp', halign='left', color=(0.627, 0.682, 0.753, 1)))
        cat_names = [c.get('n', 'Cat') for c in self.categories]
        default_cat = cat_names[category_index] if category_index < len(cat_names) else (cat_names[0] if cat_names else '')
        self.sp_cat = Spinner(text=default_cat, values=cat_names, size_hint_y=None, height='40dp')
        root.add_widget(self.sp_cat)

        # Nombre de evaluación
        root.add_widget(Label(text="Nombre", size_hint_y=None, height='20dp', halign='left', color=(0.627, 0.682, 0.753, 1)))
        self.txt_name = TextInput(text=str(item_data.get('n', '')), multiline=False, size_hint_y=None, height='40dp')
        root.add_widget(self.txt_name)

        # Nota
        root.add_widget(Label(text="Nota (vacío = pendiente)", size_hint_y=None, height='20dp', halign='left', color=(0.627, 0.682, 0.753, 1)))
        current_g = item_data.get('g')
        grade_str = "" if current_g is None else str(current_g)
        self.txt_grade = TextInput(text=grade_str, multiline=False, size_hint_y=None, height='40dp', input_filter='float')
        root.add_widget(self.txt_grade)

        # Botón Guardar
        btn_save = Button(text="Guardar", size_hint_y=None, height='44dp', background_normal='',
                          background_color=(0.337, 0.537, 0.910, 1), color=(0.063, 0.094, 0.153, 1), bold=True)
        btn_save.bind(on_release=self.save)
        root.add_widget(btn_save)

        # Botón Eliminar si es edición
        if item_index >= 0:
            btn_del = Button(text="Eliminar evaluación", size_hint_y=None, height='40dp', background_normal='',
                             background_color=(0.106, 0.149, 0.220, 1), color=(0.949, 0.651, 0.353, 1))
            btn_del.bind(on_release=self.delete)
            root.add_widget(btn_del)

        btn_cancel = Button(text="Cancelar", size_hint_y=None, height='40dp', background_normal='',
                            background_color=(0.106, 0.149, 0.220, 1), color=(0.545, 0.718, 1.0, 1))
        btn_cancel.bind(on_release=self.dismiss)
        root.add_widget(btn_cancel)

        self.add_widget(root)

    def save(self, *args):
        app = App.get_running_app()
        cat_names = [c.get('n', '') for c in self.categories]
        try:
            target_cat_idx = cat_names.index(self.sp_cat.text)
        except ValueError:
            target_cat_idx = 0

        name = self.txt_name.text.strip() or "Evaluación"
        grade_text = self.txt_grade.text.strip()
        grade = None
        if grade_text:
            try:
                grade = float(grade_text)
                if grade < 0 or grade > 10:
                    app.show_toast("La nota debe estar entre 0 y 10")
                    return
            except ValueError:
                grade = None

        self.on_save_cb(self.cat_idx, self.item_idx, target_cat_idx, name, grade)
        self.dismiss()

    def delete(self, *args):
        if self.on_delete_cb:
            self.on_delete_cb(self.cat_idx, self.item_idx)
        self.dismiss()


class CategoryModal(ModalView):
    def __init__(self, on_save_cb, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.6)
        self.auto_dismiss = True
        self.on_save_cb = on_save_cb

        root = BoxLayout(orientation='vertical', padding=16, spacing=10)
        with root.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.106, 0.149, 0.220, 1)
            rect = RoundedRectangle(pos=root.pos, size=root.size, radius=[16])
            root.bind(pos=lambda obj, val: setattr(rect, 'pos', val),
                      size=lambda obj, val: setattr(rect, 'size', val))

        root.add_widget(Label(text="[b]Nueva categoría[/b]", markup=True, font_size='18sp', size_hint_y=None, height='32dp'))

        root.add_widget(Label(text="Nombre", size_hint_y=None, height='20dp', halign='left', color=(0.627, 0.682, 0.753, 1)))
        self.txt_name = TextInput(hint_text="Ej. Talleres", multiline=False, size_hint_y=None, height='40dp')
        root.add_widget(self.txt_name)

        root.add_widget(Label(text="Peso global (%)", size_hint_y=None, height='20dp', halign='left', color=(0.627, 0.682, 0.753, 1)))
        self.txt_weight = TextInput(hint_text="20", multiline=False, size_hint_y=None, height='40dp', input_filter='int')
        root.add_widget(self.txt_weight)

        btn_create = Button(text="Crear categoría", size_hint_y=None, height='44dp', background_normal='',
                            background_color=(0.337, 0.537, 0.910, 1), color=(0.063, 0.094, 0.153, 1), bold=True)
        btn_create.bind(on_release=self.create_cat)
        root.add_widget(btn_create)

        btn_cancel = Button(text="Cancelar", size_hint_y=None, height='40dp', background_normal='',
                            background_color=(0.106, 0.149, 0.220, 1), color=(0.545, 0.718, 1.0, 1))
        btn_cancel.bind(on_release=self.dismiss)
        root.add_widget(btn_cancel)

        self.add_widget(root)

    def create_cat(self, *args):
        name = self.txt_name.text.strip() or "Nueva Categoría"
        try:
            w = float(self.txt_weight.text.strip() or 0)
        except ValueError:
            w = 0
        self.on_save_cb(name, w)
        self.dismiss()


class DetailScreen(Screen):
    subject_title = StringProperty("Física General")
    teacher_name = StringProperty("Prof. Andrade")
    current_avg = NumericProperty(8.05)
    evaluated_percent = NumericProperty(55)
    pending_percent = NumericProperty(45)
    goal_note = NumericProperty(8.5)
    min_note = NumericProperty(7.0)
    goal_status_text = StringProperty("")
    min_status_text = StringProperty("")

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        if app and hasattr(app, 'data_store'):
            self.subject_title = app.data_store.active_subject
            self.teacher_name = app.data_store.teacher
            self.goal_note = app.data_store.pgoal
            self.min_note = app.data_store.pmin
        self.refresh_detail()

    def refresh_detail(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        pc = store.calc_categories()
        avg = store.get_categories_avg()
        self.current_avg = avg
        self.evaluated_percent = pc['ev']
        self.pending_percent = pc['pend']

        # Proyecciones
        g_type, g_msg = store.calc_need(self.goal_note, pc['pts'], pc['pend'], 10.0)
        m_type, m_msg = store.calc_need(self.min_note, pc['pts'], pc['pend'], 10.0)
        self.goal_status_text = f"Objetivo {self.goal_note}: {g_msg}"
        self.min_status_text = f"Para aprobar ({self.min_note}): {m_msg}"

        container = self.ids.get('categories_container')
        if not container:
            return
        container.clear_widgets()

        for c_idx, cat in enumerate(store.categories):
            cat_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=[12, 10], spacing=6)
            cat_box.bind(minimum_height=cat_box.setter('height'))
            with cat_box.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.106, 0.149, 0.220, 1)
                r_cat = RoundedRectangle(pos=cat_box.pos, size=cat_box.size, radius=[12])
                cat_box.bind(pos=lambda obj, val, r=r_cat: setattr(r, 'pos', val),
                             size=lambda obj, val, r=r_cat: setattr(r, 'size', val))

            # Encabezado de categoría
            cat_items = cat.get('it', [])
            graded = [it for it in cat_items if it.get('g') is not None]
            avg_str = f"promedio {sum(it['g'] for it in graded)/len(graded):.2f}" if graded else "pendiente"
            header_text = f"[b]{cat.get('n', '')}[/b]  [color=a0aec0][size=12sp]{cat.get('w', 0)}% · {avg_str}[/size][/color]"

            lbl_h = Label(text=header_text, markup=True, halign='left', valign='middle',
                          size_hint_y=None, height='26dp')
            lbl_h.bind(size=lbl_h.setter('text_size'))
            cat_box.add_widget(lbl_h)

            if not cat_items:
                lbl_empty = Label(text="Sin evaluaciones aún", color=(0.627, 0.682, 0.753, 1),
                                  font_size='12sp', size_hint_y=None, height='24dp', halign='left')
                lbl_empty.bind(size=lbl_empty.setter('text_size'))
                cat_box.add_widget(lbl_empty)
            else:
                for it_idx, it in enumerate(cat_items):
                    row = BoxLayout(size_hint_y=None, height='36dp', spacing=10)
                    g_val = it.get('g')
                    g_display = f"{g_val:.1f}" if g_val is not None else "[color=a0aec0]Pendiente[/color]"
                    btn_row = Button(text=f"{it.get('n', '')}    >    {g_display}", markup=True,
                                     halign='left', valign='middle', background_normal='',
                                     background_color=(0.063, 0.094, 0.153, 0.5), color=(0.957, 0.965, 0.980, 1))
                    btn_row.bind(on_release=lambda instance, ci=c_idx, ii=it_idx: self.open_evaluation_modal(ci, ii))
                    row.add_widget(btn_row)
                    cat_box.add_widget(row)

            container.add_widget(cat_box)

    def on_goal_changed(self, text):
        try:
            val = float(text)
            self.goal_note = val
            App.get_running_app().data_store.pgoal = val
            self.refresh_detail()
        except ValueError:
            pass

    def on_min_changed(self, text):
        try:
            val = float(text)
            self.min_note = val
            App.get_running_app().data_store.pmin = val
            self.refresh_detail()
        except ValueError:
            pass

    def on_teacher_changed(self, text):
        self.teacher_name = text
        App.get_running_app().data_store.teacher = text

    def open_evaluation_modal(self, category_index=0, item_index=-1):
        modal = EvaluationModal(
            category_index=category_index,
            item_index=item_index,
            on_save_cb=self.save_evaluation,
            on_delete_cb=self.delete_evaluation
        )
        modal.open()

    def save_evaluation(self, orig_cat_idx, orig_item_idx, target_cat_idx, name, grade):
        store = App.get_running_app().data_store
        new_item = {'n': name, 'g': grade}
        if orig_item_idx >= 0 and orig_cat_idx < len(store.categories):
            items = store.categories[orig_cat_idx].get('it', [])
            if orig_item_idx < len(items):
                items.pop(orig_item_idx)
        if target_cat_idx < len(store.categories):
            store.categories[target_cat_idx].setdefault('it', []).append(new_item)
        self.refresh_detail()
        App.get_running_app().show_toast("Evaluación guardada")

    def delete_evaluation(self, cat_idx, item_idx):
        store = App.get_running_app().data_store
        if cat_idx < len(store.categories):
            items = store.categories[cat_idx].get('it', [])
            if item_idx < len(items):
                items.pop(item_idx)
        self.refresh_detail()
        App.get_running_app().show_toast("Evaluación eliminada")

    def open_new_category_modal(self):
        modal = CategoryModal(on_save_cb=self.create_category)
        modal.open()

    def create_category(self, name, weight):
        store = App.get_running_app().data_store
        store.categories.append({'n': name, 'w': weight, 'm': 'a', 'it': []})
        self.refresh_detail()
        App.get_running_app().show_toast(f"Categoría '{name}' creada")
