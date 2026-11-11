from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty
from kivy.app import App


class ProfileScreen(Screen):
    notifications_enabled = BooleanProperty(True)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        if app and hasattr(app, 'data_store'):
            self.notifications_enabled = app.data_store.global_notifications

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
