from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.app import App


class HomeScreen(Screen):
    active_class_name = StringProperty("Programación II")
    active_class_room = StringProperty("Laboratorio 3")
    active_class_time = StringProperty("En curso · hasta las 12:30")
    next_class_info = StringProperty("Próxima: Física General · 14:00 · Aula A-110")
    
    reminders_count_text = StringProperty("2 actividades")
    reminders_preview_text = StringProperty("Clase de Física General · 14:00\nDeber 4 de Programación II · 20:00")
    
    progress_percent = NumericProperty(70)
    progress_avg_text = StringProperty("Promedio general 8.92. ¡Vas muy bien, cada paso cuenta!")

    def on_pre_enter(self, *args):
        self.refresh_dashboard()

    def refresh_dashboard(self):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return

        store = app.data_store
        # Actualizar datos de progreso
        avg = store.get_general_avg()
        adv = store.get_general_adv()
        self.progress_percent = int(round(adv))
        self.progress_avg_text = f"Promedio general {avg:.2f}. ¡Vas muy bien, cada paso cuenta!"

        # Actualizar recordatorios del día
        reminders = [r for r in store.reminders if r.get('on', 0)]
        top_two = store.reminders[:2]
        self.reminders_count_text = f"{len(top_two)} actividades"
        lines = []
        for r in top_two:
            date_part = r.get('d', '').replace('Hoy · ', '')
            lines.append(f"{r.get('t', '')} · {date_part}")
        self.reminders_preview_text = "\n".join(lines) if lines else "Sin actividades pendientes para hoy."

    def navigate(self, screen_name):
        app = App.get_running_app()
        app.go_screen(screen_name)
