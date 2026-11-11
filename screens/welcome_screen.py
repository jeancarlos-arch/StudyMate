from kivy.uix.screenmanager import Screen
from kivy.app import App


class WelcomeScreen(Screen):
    def go_home(self):
        app = App.get_running_app()
        app.go_screen('home', clear_history=True)

    def go_calc(self):
        app = App.get_running_app()
        app.go_screen('calc')
