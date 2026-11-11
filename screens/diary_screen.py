from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.properties import NumericProperty, StringProperty
from kivy.app import App


class DiaryEntryModal(ModalView):
    def __init__(self, entry_index, on_save_cb, on_delete_cb, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.92, 0.85)
        self.auto_dismiss = True
        self.entry_index = entry_index
        self.on_save_cb = on_save_cb
        self.on_delete_cb = on_delete_cb

        store = App.get_running_app().data_store
        entry = store.diary_entries[entry_index] if entry_index < len(store.diary_entries) else {'d': '', 'v': []}
        questions = store.diary_questions

        from kivy.uix.scrollview import ScrollView
        scroll = ScrollView(do_scroll_x=False)
        root = BoxLayout(orientation='vertical', padding=14, spacing=8, size_hint_y=None)
        root.bind(minimum_height=root.setter('height'))

        with self.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.106, 0.149, 0.220, 1)
            rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[16])
            self.bind(pos=lambda obj, val: setattr(rect, 'pos', val),
                      size=lambda obj, val: setattr(rect, 'size', val))

        root.add_widget(Label(text=f"[b]{entry.get('d', '')}[/b]", markup=True, font_size='18sp', size_hint_y=None, height='32dp'))

        self.inputs = []
        for i, q in enumerate(questions):
            root.add_widget(Label(text=q, color=(0.627, 0.682, 0.753, 1), font_size='12sp',
                                  size_hint_y=None, height='20dp', halign='left'))
            ans = entry.get('v', [])[i] if i < len(entry.get('v', [])) else ''
            txt = TextInput(text=ans, multiline=True, size_hint_y=None, height='64dp')
            self.inputs.append(txt)
            root.add_widget(txt)

        btn_save = Button(text="Guardar cambios", size_hint_y=None, height='44dp', background_normal='',
                          background_color=(0.337, 0.537, 0.910, 1), color=(0.063, 0.094, 0.153, 1), bold=True)
        btn_save.bind(on_release=self.save)
        root.add_widget(btn_save)

        btn_del = Button(text="Eliminar entrada", size_hint_y=None, height='40dp', background_normal='',
                         background_color=(0.106, 0.149, 0.220, 1), color=(0.949, 0.651, 0.353, 1))
        btn_del.bind(on_release=self.delete)
        root.add_widget(btn_del)

        btn_cancel = Button(text="Cancelar", size_hint_y=None, height='40dp', background_normal='',
                            background_color=(0.106, 0.149, 0.220, 1), color=(0.545, 0.718, 1.0, 1))
        btn_cancel.bind(on_release=self.dismiss)
        root.add_widget(btn_cancel)

        scroll.add_widget(root)
        self.add_widget(scroll)

    def save(self, *args):
        new_values = [inp.text.strip() for inp in self.inputs]
        self.on_save_cb(self.entry_index, new_values)
        self.dismiss()

    def delete(self, *args):
        self.on_delete_cb(self.entry_index)
        self.dismiss()


class DiaryScreen(Screen):
    active_tab = NumericProperty(0)  # 0: Nueva entrada, 1: Historial
    history_tab_title = StringProperty("Historial (2)")

    def on_pre_enter(self, *args):
        self.refresh_diary_view()

    def set_tab(self, tab_index):
        self.active_tab = tab_index
        self.refresh_diary_view()

    def refresh_diary_view(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        entries = store.diary_entries
        self.history_tab_title = f"Historial ({len(entries)})"

        container = self.ids.get('diary_container')
        if not container:
            return
        container.clear_widgets()

        if self.active_tab == 0:
            # Vista Nueva Entrada
            self.input_widgets = []
            for q in store.diary_questions:
                lbl = Label(text=q, color=(0.627, 0.682, 0.753, 1), font_size='12sp',
                            size_hint_y=None, height='24dp', halign='left', valign='bottom')
                lbl.bind(size=lbl.setter('text_size'))
                txt = TextInput(multiline=True, size_hint_y=None, height='68dp')
                self.input_widgets.append(txt)
                container.add_widget(lbl)
                container.add_widget(txt)

            btn_save = Button(text="Guardar entrada", size_hint_y=None, height='46dp',
                              background_normal='', background_color=(0.337, 0.537, 0.910, 1),
                              color=(0.063, 0.094, 0.153, 1), bold=True, font_size='15sp')
            btn_save.bind(on_release=lambda x: self.save_new_entry())
            container.add_widget(btn_save)

        else:
            # Vista Historial
            if not entries:
                lbl_empty = Label(text="Aún no hay entradas. Cuando quieras, escribe la primera.",
                                  color=(0.627, 0.682, 0.753, 1), font_size='13sp', size_hint_y=None, height='60dp')
                container.add_widget(lbl_empty)
                return

            for idx, entry in enumerate(entries):
                card = BoxLayout(orientation='vertical', size_hint_y=None, height='92dp', padding=[14, 10], spacing=4)
                with card.canvas.before:
                    from kivy.graphics import Color, RoundedRectangle
                    Color(0.106, 0.149, 0.220, 1)
                    r_c = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
                    card.bind(pos=lambda obj, val, r=r_c: setattr(r, 'pos', val),
                              size=lambda obj, val, r=r_c: setattr(r, 'size', val))

                row_t = BoxLayout(size_hint_y=None, height='22dp')
                lbl_date = Label(text=f"[b]{entry.get('d', '')}[/b]", markup=True, halign='left',
                                 color=(0.957, 0.965, 0.980, 1), font_size='14sp')
                lbl_date.bind(size=lbl_date.setter('text_size'))
                lbl_icon = Label(text="✎", color=(0.545, 0.718, 1.0, 1), size_hint_x=None, width='24dp')
                row_t.add_widget(lbl_date)
                row_t.add_widget(lbl_icon)

                first_val = entry.get('v', [''])[0] if entry.get('v') else ''
                logro_val = entry.get('v', ['','','','',''])[4] if len(entry.get('v', [])) > 4 else ''

                lbl_sum = Label(text=first_val, color=(0.627, 0.682, 0.753, 1), font_size='12sp',
                                halign='left', size_hint_y=None, height='20dp')
                lbl_sum.bind(size=lbl_sum.setter('text_size'))

                lbl_logro = Label(text=f"Logro: {logro_val}", color=(0.224, 0.788, 0.541, 1), font_size='12sp',
                                  halign='left', size_hint_y=None, height='20dp')
                lbl_logro.bind(size=lbl_logro.setter('text_size'))

                card.add_widget(row_t)
                card.add_widget(lbl_sum)
                card.add_widget(lbl_logro)

                from kivy.uix.relativelayout import RelativeLayout
                rl = RelativeLayout(size_hint_y=None, height='92dp')
                btn_click = Button(background_color=(0,0,0,0), size_hint=(1, 1))
                btn_click.bind(on_release=lambda x, i=idx: self.open_entry_modal(i))
                rl.add_widget(card)
                rl.add_widget(btn_click)
                container.add_widget(rl)

    def save_new_entry(self):
        answers = [txt.text.strip() for txt in self.input_widgets]
        if not any(answers):
            App.get_running_app().show_toast("Escribe al menos una respuesta")
            return

        store = App.get_running_app().data_store
        new_entry = {'d': 'Hoy · 2 nov 2026', 'v': answers}
        store.diary_entries.insert(0, new_entry)

        App.get_running_app().show_toast("Entrada guardada")
        self.set_tab(1)

    def open_entry_modal(self, entry_index):
        modal = DiaryEntryModal(
            entry_index=entry_index,
            on_save_cb=self.update_entry,
            on_delete_cb=self.delete_entry
        )
        modal.open()

    def update_entry(self, entry_index, new_values):
        store = App.get_running_app().data_store
        if entry_index < len(store.diary_entries):
            store.diary_entries[entry_index]['v'] = new_values
        self.refresh_diary_view()
        App.get_running_app().show_toast("Cambios guardados")

    def delete_entry(self, entry_index):
        store = App.get_running_app().data_store
        if entry_index < len(store.diary_entries):
            store.diary_entries.pop(entry_index)
        self.refresh_diary_view()
        App.get_running_app().show_toast("Entrada eliminada")
