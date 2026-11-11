from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.uix.modalview import ModalView
from kivy.app import App


class ReminderModal(ModalView):
    def __init__(self, reminder_index, on_save_cb, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, 0.55)
        self.auto_dismiss = True
        self.reminder_index = reminder_index
        self.on_save_cb = on_save_cb

        store = App.get_running_app().data_store
        item = store.reminders[reminder_index] if reminder_index < len(store.reminders) else {}

        root = BoxLayout(orientation='vertical', padding=16, spacing=12)
        with root.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0.106, 0.149, 0.220, 1)
            rect = RoundedRectangle(pos=root.pos, size=root.size, radius=[16])
            root.bind(pos=lambda obj, val: setattr(rect, 'pos', val),
                      size=lambda obj, val: setattr(rect, 'size', val))

        root.add_widget(Label(text=f"[b]{item.get('t', '')}[/b]", markup=True, font_size='16sp',
                              size_hint_y=None, height='28dp', halign='left'))
        root.add_widget(Label(text=item.get('d', ''), color=(0.627, 0.682, 0.753, 1), font_size='12sp',
                              size_hint_y=None, height='20dp', halign='left'))

        # Switch Recordarme
        row_sw = BoxLayout(size_hint_y=None, height='40dp')
        row_sw.add_widget(Label(text="Recordarme", halign='left', valign='middle'))
        self.sw_active = Switch(active=bool(item.get('on', 0)), size_hint_x=None, width='80dp')
        row_sw.add_widget(self.sw_active)
        root.add_widget(row_sw)

        # Spinner Cuánto antes
        root.add_widget(Label(text="Cuánto antes", font_size='12sp', color=(0.627, 0.682, 0.753, 1),
                              size_hint_y=None, height='20dp', halign='left'))
        options_map = {10: '10 minutos', 30: '30 minutos', 60: '1 hora', 1440: '1 día'}
        rev_map = {v: k for k, v in options_map.items()}
        current_m = item.get('m', 30)
        curr_text = options_map.get(current_m, '30 minutos')

        self.sp_time = Spinner(text=curr_text, values=list(rev_map.keys()), size_hint_y=None, height='42dp')
        root.add_widget(self.sp_time)

        btn_done = Button(text="Listo", size_hint_y=None, height='44dp', background_normal='',
                          background_color=(0.337, 0.537, 0.910, 1), color=(0.063, 0.094, 0.153, 1), bold=True)
        btn_done.bind(on_release=lambda x: self.save(rev_map))
        root.add_widget(btn_done)

        self.add_widget(root)

    def save(self, rev_map):
        is_on = 1 if self.sw_active.active else 0
        minutes = rev_map.get(self.sp_time.text, 30)
        self.on_save_cb(self.reminder_index, is_on, minutes)
        self.dismiss()


class RemindScreen(Screen):
    def on_pre_enter(self, *args):
        self.refresh_reminders()

    def refresh_reminders(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        container = self.ids.get('reminders_container')
        if not container:
            return
        container.clear_widgets()

        for idx, item in enumerate(store.reminders):
            card = BoxLayout(orientation='horizontal', size_hint_y=None, height='74dp', padding=[14, 10], spacing=8)
            with card.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.106, 0.149, 0.220, 1)
                r_c = RoundedRectangle(pos=card.pos, size=card.size, radius=[12])
                card.bind(pos=lambda obj, val, r=r_c: setattr(r, 'pos', val),
                          size=lambda obj, val, r=r_c: setattr(r, 'size', val))

            # Columna Izquierda (Título y Fecha)
            col_l = BoxLayout(orientation='vertical', spacing=2)
            lbl_title = Label(text=f"[b]{item.get('t', '')}[/b]", markup=True, halign='left', valign='middle',
                              color=(0.957, 0.965, 0.980, 1), font_size='14sp')
            lbl_title.bind(size=lbl_title.setter('text_size'))
            lbl_date = Label(text=item.get('d', ''), halign='left', valign='middle',
                             color=(0.627, 0.682, 0.753, 1), font_size='12sp')
            lbl_date.bind(size=lbl_date.setter('text_size'))
            col_l.add_widget(lbl_title)
            col_l.add_widget(lbl_date)

            # Columna Derecha (Icono y Aviso)
            col_r = BoxLayout(orientation='vertical', size_hint_x=None, width='90dp', spacing=2)
            is_on = bool(item.get('on', 0))
            bell_color = "8bb7ff" if is_on else "a0aec0"
            m = item.get('m', 30)
            if is_on:
                time_str = "1 día antes" if m == 1440 else (f"{m} min antes" if m < 60 else "1 hora antes")
            else:
                time_str = "Sin aviso"

            lbl_bell = Label(text=f"[color={bell_color}]🔔[/color]", markup=True, halign='right', font_size='16sp')
            lbl_bell.bind(size=lbl_bell.setter('text_size'))
            lbl_time = Label(text=f"[color={bell_color}]{time_str}[/color]", markup=True, halign='right', font_size='11sp')
            lbl_time.bind(size=lbl_time.setter('text_size'))
            col_r.add_widget(lbl_bell)
            col_r.add_widget(lbl_time)

            card.add_widget(col_l)
            card.add_widget(col_r)

            from kivy.uix.relativelayout import RelativeLayout
            rl = RelativeLayout(size_hint_y=None, height='74dp')
            btn_click = Button(background_color=(0,0,0,0), size_hint=(1, 1))
            btn_click.bind(on_release=lambda x, i=idx: self.open_reminder_modal(i))
            rl.add_widget(card)
            rl.add_widget(btn_click)
            container.add_widget(rl)

    def open_reminder_modal(self, reminder_index):
        modal = ReminderModal(
            reminder_index=reminder_index,
            on_save_cb=self.save_reminder_config
        )
        modal.open()

    def save_reminder_config(self, index, is_on, minutes):
        store = App.get_running_app().data_store
        if index < len(store.reminders):
            store.reminders[index]['on'] = is_on
            store.reminders[index]['m'] = minutes
        self.refresh_reminders()
        App.get_running_app().show_toast("Recordatorio configurado")
