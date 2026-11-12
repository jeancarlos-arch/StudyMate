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
    def __init__(self, categories, category_index, item_index, on_save_cb, on_delete_cb=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.72)
        self.auto_dismiss = True
        self.background_color = (0, 0, 0, 0.75)

        self.categories = categories
        self.cat_idx = category_index
        self.item_idx = item_index
        self.on_save_cb = on_save_cb
        self.on_delete_cb = on_delete_cb

        item_data = {}
        if 0 <= category_index < len(self.categories):
            items = self.categories[category_index].get('it', [])
            if 0 <= item_index < len(items):
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
        root.add_widget(Label(text="Categoría / Rubro", size_hint_y=None, height='18dp', halign='left', color=(0.627, 0.682, 0.753, 1)))
        cat_names = [c.get('n', f'Categoría {i+1}') for i, c in enumerate(self.categories)]
        default_cat = cat_names[category_index] if 0 <= category_index < len(cat_names) else (cat_names[0] if cat_names else 'Sin categorías')
        self.sp_cat = Spinner(text=default_cat, values=cat_names, size_hint_y=None, height='38dp')
        root.add_widget(self.sp_cat)

        # Nombre de evaluación
        root.add_widget(Label(text="Nombre de la evaluación *", size_hint_y=None, height='18dp', halign='left', color=(0.627, 0.682, 0.753, 1)))
        self.txt_name = TextInput(
            text=str(item_data.get('n', '')),
            hint_text="Ej: Deber 1, Examen Parcial",
            multiline=False, size_hint_y=None, height='38dp',
            background_normal='', background_color=(0.063, 0.094, 0.153, 1),
            foreground_color=(0.957, 0.965, 0.980, 1), cursor_color=(0.545, 0.718, 1.0, 1)
        )
        root.add_widget(self.txt_name)

        # Nota
        root.add_widget(Label(text="Nota obtenida (deja vacío si aún está pendiente)", size_hint_y=None, height='18dp', halign='left', color=(0.627, 0.682, 0.753, 1)))
        current_g = item_data.get('g')
        grade_str = "" if current_g is None else str(current_g)
        self.txt_grade = TextInput(
            text=grade_str,
            hint_text="Ej: 8.5 (o vacío)",
            multiline=False, size_hint_y=None, height='38dp', input_filter='float',
            background_normal='', background_color=(0.063, 0.094, 0.153, 1),
            foreground_color=(0.957, 0.965, 0.980, 1), cursor_color=(0.545, 0.718, 1.0, 1)
        )
        root.add_widget(self.txt_grade)

        # Botón Guardar
        btn_save = Button(
            text="Guardar evaluación", size_hint_y=None, height='44dp', background_normal='',
            background_color=(0.337, 0.537, 0.910, 1), color=(0.063, 0.094, 0.153, 1), bold=True
        )
        btn_save.bind(on_release=self.save)
        root.add_widget(btn_save)

        # Botón Eliminar si es edición
        if item_index >= 0:
            btn_del = Button(
                text="Eliminar evaluación", size_hint_y=None, height='38dp', background_normal='',
                background_color=(0.173, 0.227, 0.322, 0.7), color=(0.949, 0.651, 0.353, 1)
            )
            btn_del.bind(on_release=self.delete)
            root.add_widget(btn_del)

        btn_cancel = Button(
            text="Cancelar", size_hint_y=None, height='38dp', background_normal='',
            background_color=(0.106, 0.149, 0.220, 1), color=(0.545, 0.718, 1.0, 1)
        )
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

        name = self.txt_name.text.strip()
        if not name:
            app.show_toast("Escribe el nombre de la evaluación")
            return

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
        self.size_hint = (0.9, 0.58)
        self.auto_dismiss = True
        self.background_color = (0, 0, 0, 0.75)
        self.on_save_cb = on_save_cb

        root = BoxLayout(orientation='vertical', padding=16, spacing=10)
        with root.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.106, 0.149, 0.220, 1)
            rect = RoundedRectangle(pos=root.pos, size=root.size, radius=[16])
            root.bind(pos=lambda obj, val: setattr(rect, 'pos', val),
                      size=lambda obj, val: setattr(rect, 'size', val))

        root.add_widget(Label(text="[b]Nueva categoría / Rubro[/b]", markup=True, font_size='18sp', size_hint_y=None, height='32dp'))

        root.add_widget(Label(text="Nombre del rubro *", size_hint_y=None, height='18dp', halign='left', color=(0.627, 0.682, 0.753, 1)))
        self.txt_name = TextInput(
            hint_text="Ej: Parciales, Deberes, Talleres, Proyecto", multiline=False, size_hint_y=None, height='38dp',
            background_normal='', background_color=(0.063, 0.094, 0.153, 1),
            foreground_color=(0.957, 0.965, 0.980, 1), cursor_color=(0.545, 0.718, 1.0, 1)
        )
        root.add_widget(self.txt_name)

        root.add_widget(Label(text="Peso en la nota final (%) *", size_hint_y=None, height='18dp', halign='left', color=(0.627, 0.682, 0.753, 1)))
        self.txt_weight = TextInput(
            hint_text="Ej: 30", multiline=False, size_hint_y=None, height='38dp', input_filter='float',
            background_normal='', background_color=(0.063, 0.094, 0.153, 1),
            foreground_color=(0.957, 0.965, 0.980, 1), cursor_color=(0.545, 0.718, 1.0, 1)
        )
        root.add_widget(self.txt_weight)

        btn_create = Button(
            text="Crear categoría", size_hint_y=None, height='44dp', background_normal='',
            background_color=(0.337, 0.537, 0.910, 1), color=(0.063, 0.094, 0.153, 1), bold=True
        )
        btn_create.bind(on_release=self.create_cat)
        root.add_widget(btn_create)

        btn_cancel = Button(
            text="Cancelar", size_hint_y=None, height='38dp', background_normal='',
            background_color=(0.106, 0.149, 0.220, 1), color=(0.545, 0.718, 1.0, 1)
        )
        btn_cancel.bind(on_release=self.dismiss)
        root.add_widget(btn_cancel)

        self.add_widget(root)

    def create_cat(self, *args):
        app = App.get_running_app()
        name = self.txt_name.text.strip()
        if not name:
            app.show_toast("Escribe el nombre de la categoría")
            return

        try:
            w = float(self.txt_weight.text.strip() or 0)
        except ValueError:
            w = 0.0

        if w <= 0:
            app.show_toast("El peso porcentual debe ser mayor a 0")
            return

        self.on_save_cb(name, w)
        self.dismiss()


class DetailScreen(Screen):
    subject_title = StringProperty("Materia")
    teacher_name = StringProperty("")
    current_avg = NumericProperty(0.0)
    evaluated_percent = NumericProperty(0.0)
    pending_percent = NumericProperty(100.0)
    goal_note = NumericProperty(8.5)
    min_note = NumericProperty(7.0)
    goal_status_text = StringProperty("")
    min_status_text = StringProperty("")

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        if app and hasattr(app, 'data_store'):
            subj = app.data_store.get_active_subject_obj()
            if subj:
                self.subject_title = subj.get('n', 'Materia')
                self.teacher_name = subj.get('teacher', '')
                self.goal_note = float(subj.get('pgoal', 8.5))
                self.min_note = float(subj.get('pmin', 7.0))
            else:
                self.subject_title = "Sin materia seleccionada"
                self.teacher_name = ""
        self.refresh_detail()

    def get_current_subject(self):
        app = App.get_running_app()
        if app and hasattr(app, 'data_store'):
            return app.data_store.get_active_subject_obj()
        return None

    def refresh_detail(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        subj = self.get_current_subject()
        container = self.ids.get('categories_container')
        if not container:
            return
        container.clear_widgets()

        if not subj:
            self.subject_title = "Sin materia seleccionada"
            self.current_avg = 0.0
            self.evaluated_percent = 0.0
            self.pending_percent = 100.0
            self.goal_status_text = "Selecciona una materia desde la lista."
            self.min_status_text = ""
            return

        categories = subj.setdefault('categories', [])
        store = app.data_store
        pc = store.calc_categories_for(categories)

        self.current_avg = (pc['pts'] / pc['ev'] * 100.0) if pc['ev'] > 0 else 0.0
        self.evaluated_percent = pc['ev']
        self.pending_percent = pc['pend']

        # Proyecciones
        _, g_msg = store.calc_need(self.goal_note, pc['pts'], pc['pend'], 10.0)
        _, m_msg = store.calc_need(self.min_note, pc['pts'], pc['pend'], 10.0)
        self.goal_status_text = f"Objetivo ({self.goal_note:.1f}): {g_msg}"
        self.min_status_text = f"Para aprobar ({self.min_note:.1f}): {m_msg}"

        if not categories:
            empty_box = BoxLayout(orientation='vertical', size_hint_y=None, height='100dp', padding=[16, 16], spacing=6)
            with empty_box.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.106, 0.149, 0.220, 0.6)
                r_c = RoundedRectangle(pos=empty_box.pos, size=empty_box.size, radius=[12])
                empty_box.bind(pos=lambda obj, val, r=r_c: setattr(r, 'pos', val),
                               size=lambda obj, val, r=r_c: setattr(r, 'size', val))

            lbl1 = Label(text="[b]Sin categorías de evaluación todavía[/b]", markup=True,
                         color=(0.957, 0.965, 0.980, 1), font_size='14sp', size_hint_y=None, height='24dp')
            lbl2 = Label(text="Pulsa '+ Nueva categoría' para definir cómo se divide tu nota (ej. Parciales 50%, Deberes 20%, Proyecto 30%).",
                         color=(0.627, 0.682, 0.753, 1), font_size='12sp', size_hint_y=None, height='32dp')
            empty_box.add_widget(lbl1)
            empty_box.add_widget(lbl2)
            container.add_widget(empty_box)
            return

        for c_idx, cat in enumerate(categories):
            cat_box = BoxLayout(orientation='vertical', size_hint_y=None, padding=[14, 10], spacing=6)
            cat_box.bind(minimum_height=cat_box.setter('height'))
            with cat_box.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.106, 0.149, 0.220, 1)
                r_cat = RoundedRectangle(pos=cat_box.pos, size=cat_box.size, radius=[12])
                cat_box.bind(pos=lambda obj, val, r=r_cat: setattr(r, 'pos', val),
                             size=lambda obj, val, r=r_cat: setattr(r, 'size', val))

            # Fila de Encabezado de categoría con botón para borrar categoría
            header_row = BoxLayout(size_hint_y=None, height='28dp', spacing=6)
            cat_items = cat.get('it', [])
            graded = [it for it in cat_items if it.get('g') is not None]
            avg_str = f"promedio {sum(float(it['g']) for it in graded)/len(graded):.2f}" if graded else "sin calificar"
            header_text = f"[b]{cat.get('n', '')}[/b]  [color=a0aec0][size=12sp]{cat.get('w', 0)}% · {avg_str}[/size][/color]"

            lbl_h = Label(text=header_text, markup=True, halign='left', valign='middle')
            lbl_h.bind(size=lbl_h.setter('text_size'))

            btn_del_cat = Button(
                text="✕", size_hint=(None, None), size=('26dp', '26dp'),
                background_normal='', background_color=(0, 0, 0, 0),
                color=(0.949, 0.651, 0.353, 1), font_size='13sp'
            )
            btn_del_cat.bind(on_release=lambda x, ci=c_idx: self.delete_category(ci))

            header_row.add_widget(lbl_h)
            header_row.add_widget(btn_del_cat)
            cat_box.add_widget(header_row)

            if not cat_items:
                lbl_empty = Label(text="Sin evaluaciones aún en este rubro.", color=(0.627, 0.682, 0.753, 1),
                                  font_size='12sp', size_hint_y=None, height='24dp', halign='left')
                lbl_empty.bind(size=lbl_empty.setter('text_size'))
                cat_box.add_widget(lbl_empty)
            else:
                for it_idx, it in enumerate(cat_items):
                    row = BoxLayout(size_hint_y=None, height='36dp', spacing=10)
                    g_val = it.get('g')
                    g_display = f"{float(g_val):.2f}" if g_val is not None else "[color=a0aec0]Pendiente[/color]"
                    btn_row = Button(
                        text=f"  {it.get('n', '')}   ➔   {g_display}", markup=True,
                        halign='left', valign='middle', background_normal='',
                        background_color=(0.063, 0.094, 0.153, 0.7), color=(0.957, 0.965, 0.980, 1),
                        font_size='13sp'
                    )
                    btn_row.bind(on_release=lambda instance, ci=c_idx, ii=it_idx: self.open_evaluation_modal(ci, ii))
                    row.add_widget(btn_row)
                    cat_box.add_widget(row)

            container.add_widget(cat_box)

    def on_goal_changed(self, text):
        try:
            val = float(text)
            self.goal_note = val
            subj = self.get_current_subject()
            if subj:
                subj['pgoal'] = val
            self.refresh_detail()
        except ValueError:
            pass

    def on_min_changed(self, text):
        try:
            val = float(text)
            self.min_note = val
            subj = self.get_current_subject()
            if subj:
                subj['pmin'] = val
            self.refresh_detail()
        except ValueError:
            pass

    def on_teacher_changed(self, text):
        self.teacher_name = text
        subj = self.get_current_subject()
        if subj:
            subj['teacher'] = text

    def open_evaluation_modal(self, category_index=0, item_index=-1):
        subj = self.get_current_subject()
        if not subj or not subj.get('categories'):
            App.get_running_app().show_toast("Primero debes crear al menos una categoría con '+ Nueva categoría'")
            return

        modal = EvaluationModal(
            categories=subj['categories'],
            category_index=category_index,
            item_index=item_index,
            on_save_cb=self.save_evaluation,
            on_delete_cb=self.delete_evaluation
        )
        modal.open()

    def save_evaluation(self, orig_cat_idx, orig_item_idx, target_cat_idx, name, grade):
        subj = self.get_current_subject()
        if not subj:
            return

        categories = subj.setdefault('categories', [])
        new_item = {'n': name, 'g': grade}

        if orig_item_idx >= 0 and 0 <= orig_cat_idx < len(categories):
            items = categories[orig_cat_idx].get('it', [])
            if orig_item_idx < len(items):
                items.pop(orig_item_idx)

        if 0 <= target_cat_idx < len(categories):
            categories[target_cat_idx].setdefault('it', []).append(new_item)

        self.refresh_detail()
        App.get_running_app().show_toast(f"Evaluación '{name}' guardada")

    def delete_evaluation(self, cat_idx, item_idx):
        subj = self.get_current_subject()
        if not subj:
            return

        categories = subj.get('categories', [])
        if 0 <= cat_idx < len(categories):
            items = categories[cat_idx].get('it', [])
            if 0 <= item_idx < len(items):
                name = items[item_idx].get('n', '')
                items.pop(item_idx)
                App.get_running_app().show_toast(f"Evaluación '{name}' eliminada")

        self.refresh_detail()

    def open_new_category_modal(self):
        subj = self.get_current_subject()
        if not subj:
            App.get_running_app().show_toast("No hay materia seleccionada")
            return
        modal = CategoryModal(on_save_cb=self.create_category)
        modal.open()

    def create_category(self, name, weight):
        subj = self.get_current_subject()
        if not subj:
            return

        subj.setdefault('categories', []).append({
            'n': name,
            'w': weight,
            'm': 'a',
            'it': []
        })
        self.refresh_detail()
        App.get_running_app().show_toast(f"Categoría '{name}' ({weight}%) creada")

    def delete_category(self, cat_idx):
        subj = self.get_current_subject()
        if not subj:
            return

        categories = subj.get('categories', [])
        if 0 <= cat_idx < len(categories):
            cat_name = categories[cat_idx].get('n', '')
            categories.pop(cat_idx)
            self.refresh_detail()
            App.get_running_app().show_toast(f"Categoría '{cat_name}' eliminada")
