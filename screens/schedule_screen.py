from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.modalview import ModalView
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.app import App


class ClassModal(ModalView):
    def __init__(self, day_index, class_index, on_save_cb, on_delete_cb=None, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.65)
        self.auto_dismiss = True
        self.day_index = day_index
        self.class_index = class_index
        self.on_save_cb = on_save_cb
        self.on_delete_cb = on_delete_cb

        store = App.get_running_app().data_store
        class_data = {}
        if class_index >= 0 and day_index < len(store.schedule):
            day_classes = store.schedule[day_index]
            if class_index < len(day_classes):
                class_data = day_classes[class_index]

        root = BoxLayout(orientation='vertical', padding=16, spacing=10)
        with root.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.106, 0.149, 0.220, 1)
            rect = RoundedRectangle(pos=root.pos, size=root.size, radius=[16])
            root.bind(pos=lambda obj, val: setattr(rect, 'pos', val),
                      size=lambda obj, val: setattr(rect, 'size', val))

        title = "Editar clase" if class_index >= 0 else "Agregar clase"
        root.add_widget(Label(text=f"[b]{title}[/b]", markup=True, font_size='18sp', size_hint_y=None, height='32dp'))

        root.add_widget(Label(text="Materia", size_hint_y=None, height='20dp', halign='left', color=(0.627, 0.682, 0.753, 1)))
        self.txt_name = TextInput(text=str(class_data.get('n', '')), multiline=False, size_hint_y=None, height='40dp')
        root.add_widget(self.txt_name)

        root.add_widget(Label(text="Horario (ej. 08:00 – 10:00)", size_hint_y=None, height='20dp', halign='left', color=(0.627, 0.682, 0.753, 1)))
        self.txt_time = TextInput(text=str(class_data.get('h', '')), multiline=False, size_hint_y=None, height='40dp')
        root.add_widget(self.txt_time)

        root.add_widget(Label(text="Aula (ej. B-204)", size_hint_y=None, height='20dp', halign='left', color=(0.627, 0.682, 0.753, 1)))
        self.txt_room = TextInput(text=str(class_data.get('a', '')), multiline=False, size_hint_y=None, height='40dp')
        root.add_widget(self.txt_room)

        btn_save = Button(text="Guardar", size_hint_y=None, height='44dp', background_normal='',
                          background_color=(0.337, 0.537, 0.910, 1), color=(0.063, 0.094, 0.153, 1), bold=True)
        btn_save.bind(on_release=self.save)
        root.add_widget(btn_save)

        if class_index >= 0:
            btn_del = Button(text="Eliminar clase", size_hint_y=None, height='40dp', background_normal='',
                             background_color=(0.106, 0.149, 0.220, 1), color=(0.949, 0.651, 0.353, 1))
            btn_del.bind(on_release=self.delete)
            root.add_widget(btn_del)

        btn_cancel = Button(text="Cancelar", size_hint_y=None, height='40dp', background_normal='',
                            background_color=(0.106, 0.149, 0.220, 1), color=(0.545, 0.718, 1.0, 1))
        btn_cancel.bind(on_release=self.dismiss)
        root.add_widget(btn_cancel)

        self.add_widget(root)

    def save(self, *args):
        name = self.txt_name.text.strip() or "Materia"
        time_str = self.txt_time.text.strip() or "08:00 – 10:00"
        room = self.txt_room.text.strip() or "Por definir"
        self.on_save_cb(self.day_index, self.class_index, name, time_str, room)
        self.dismiss()

    def delete(self, *args):
        if self.on_delete_cb:
            self.on_delete_cb(self.day_index, self.class_index)
        self.dismiss()


class ScheduleScreen(Screen):
    week_offset = NumericProperty(0)
    current_day_idx = NumericProperty(0)  # 0: Lun, 1: Mar, 2: Mié, 3: Jue, 4: Vie
    week_range_text = StringProperty("2 nov – 6 nov 2026")
    class_reminder_active = BooleanProperty(True)

    def on_pre_enter(self, *args):
        self.update_week_text()
        self.refresh_classes()

    def update_week_text(self):
        # Base: Semana 2 al 6 de noviembre 2026
        base_start = 2 + (self.week_offset * 7)
        base_end = 6 + (self.week_offset * 7)
        self.week_range_text = f"{base_start} nov – {base_end} nov 2026"

    def prev_week(self):
        self.week_offset -= 1
        self.update_week_text()
        self.refresh_classes()

    def next_week(self):
        self.week_offset += 1
        self.update_week_text()
        self.refresh_classes()

    def select_day(self, day_index):
        self.current_day_idx = day_index
        self.refresh_classes()

    def refresh_classes(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        container = self.ids.get('classes_container')
        if not container:
            return
        container.clear_widgets()

        if self.current_day_idx < len(store.schedule):
            classes = store.schedule[self.current_day_idx]
        else:
            classes = []

        if not classes:
            empty_box = BoxLayout(orientation='vertical', size_hint_y=None, height='80dp', padding=12)
            lbl = Label(text="Sin clases este día. ¡Buen momento para descansar o repasar!",
                        color=(0.627, 0.682, 0.753, 1), font_size='13sp', halign='center', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            empty_box.add_widget(lbl)
            container.add_widget(empty_box)
            return

        for idx, c in enumerate(classes):
            card = BoxLayout(orientation='vertical', size_hint_y=None, height='84dp', padding=[14, 10], spacing=4)
            with card.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.106, 0.149, 0.220, 1)
                r_bg = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
                card.bind(pos=lambda obj, val, r=r_bg: setattr(r, 'pos', val),
                          size=lambda obj, val, r=r_bg: setattr(r, 'size', val))

            top_row = BoxLayout(size_hint_y=None, height='20dp')
            lbl_time = Label(text=c.get('h', ''), color=(0.627, 0.682, 0.753, 1), font_size='12sp',
                             halign='left', valign='middle')
            lbl_time.bind(size=lbl_time.setter('text_size'))
            top_row.add_widget(lbl_time)

            # Badge si aplica
            if self.week_offset == 0 and self.current_day_idx == 0:
                if idx == 1:
                    badge = Label(text="[color=101827][b] En curso [/b][/color]", markup=True,
                                  size_hint_x=None, width='76dp', font_size='11sp')
                    with badge.canvas.before:
                        from kivy.graphics import Color as GColor, RoundedRectangle as GRect
                        GColor(0.224, 0.788, 0.541, 1)
                        GRect(pos=badge.pos, size=badge.size, radius=[6])
                    top_row.add_widget(badge)
                elif idx == 2:
                    badge = Label(text="[color=101827][b] Próxima [/b][/color]", markup=True,
                                  size_hint_x=None, width='70dp', font_size='11sp')
                    with badge.canvas.before:
                        from kivy.graphics import Color as GColor, RoundedRectangle as GRect
                        GColor(0.545, 0.718, 1.0, 1)
                        GRect(pos=badge.pos, size=badge.size, radius=[6])
                    top_row.add_widget(badge)

            lbl_name = Label(text=f"[b]{c.get('n', '')}[/b]", markup=True, color=(0.957, 0.965, 0.980, 1),
                             font_size='15sp', halign='left', valign='middle', size_hint_y=None, height='24dp')
            lbl_name.bind(size=lbl_name.setter('text_size'))

            lbl_room = Label(text=f"Aula {c.get('a', '')}", color=(0.627, 0.682, 0.753, 1),
                             font_size='12sp', halign='left', valign='middle', size_hint_y=None, height='18dp')
            lbl_room.bind(size=lbl_room.setter('text_size'))

            card.add_widget(top_row)
            card.add_widget(lbl_name)
            card.add_widget(lbl_room)

            from kivy.uix.relativelayout import RelativeLayout
            rl = RelativeLayout(size_hint_y=None, height='84dp')
            btn_click = Button(background_color=(0,0,0,0), size_hint=(1, 1))
            btn_click.bind(on_release=lambda instance, i=idx: self.open_class_modal(i))
            rl.add_widget(card)
            rl.add_widget(btn_click)
            container.add_widget(rl)

    def open_class_modal(self, class_index=-1):
        modal = ClassModal(
            day_index=self.current_day_idx,
            class_index=class_index,
            on_save_cb=self.save_class,
            on_delete_cb=self.delete_class
        )
        modal.open()

    def save_class(self, day_idx, class_idx, name, time_str, room):
        store = App.get_running_app().data_store
        new_class = {'n': name, 'h': time_str, 'a': room}
        if day_idx < len(store.schedule):
            if class_idx >= 0 and class_idx < len(store.schedule[day_idx]):
                store.schedule[day_idx][class_idx] = new_class
            else:
                store.schedule[day_idx].append(new_class)
            store.schedule[day_idx].sort(key=lambda x: x.get('h', ''))
        self.refresh_classes()
        App.get_running_app().show_toast("Clase guardada")

    def delete_class(self, day_idx, class_idx):
        store = App.get_running_app().data_store
        if day_idx < len(store.schedule) and class_idx < len(store.schedule[day_idx]):
            store.schedule[day_idx].pop(class_idx)
        self.refresh_classes()
        App.get_running_app().show_toast("Clase eliminada")

    def toggle_reminder(self):
        self.class_reminder_active = not self.class_reminder_active
        msg = "Te avisaremos 30 min antes de cada clase." if self.class_reminder_active else "Notificaciones de clase desactivadas."
        App.get_running_app().show_toast(msg)

    def go_import(self):
        App.get_running_app().go_screen('import_schedule')
