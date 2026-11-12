from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty, StringProperty
from kivy.app import App


class ProfileScreen(Screen):
    notifications_enabled = BooleanProperty(True)
    user_name = StringProperty("Estudiante")
    user_career_sem = StringProperty("Toca abajo para registrar tus datos")
    avatar_initial = StringProperty("👤")

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        if app and hasattr(app, 'data_store'):
            store = app.data_store
            self.notifications_enabled = store.global_notifications

            name = store.student_name.strip() if store.student_name else ""
            if name:
                self.user_name = name
                self.avatar_initial = name[0].upper()
            else:
                self.user_name = "Estudiante"
                self.avatar_initial = "👤"

            career = store.student_career.strip() if store.student_career else ""
            sem = store.student_semester.strip() if store.student_semester else ""
            if career and sem:
                self.user_career_sem = f"{career} · {sem}"
            elif career or sem:
                self.user_career_sem = f"{career}{sem}"
            else:
                self.user_career_sem = "Toca abajo para registrar tus datos"

    def toggle_notifications(self, is_active):
        self.notifications_enabled = is_active
        app = App.get_running_app()
        if app and hasattr(app, 'data_store'):
            app.data_store.global_notifications = is_active
        msg = "Notificaciones activadas" if is_active else "Notificaciones desactivadas"
        app.show_toast(msg)

    def navigate(self, screen_name):
        app = App.get_running_app()
        app.go_screen(screen_name)
