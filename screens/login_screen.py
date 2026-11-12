from kivy.uix.screenmanager import Screen
from kivy.app import App


class LoginScreen(Screen):
    def on_pre_enter(self, *args):
        app = App.get_running_app()
        if not app or not hasattr(app, 'data_store'):
            return
        store = app.data_store

        # Cargar valores actuales en los campos si ya fueron asignados
        if 'input_name' in self.ids and store.student_name:
            self.ids.input_name.text = store.student_name
        if 'input_career' in self.ids and store.student_career:
            self.ids.input_career.text = store.student_career
        if 'input_semester' in self.ids and store.student_semester:
            self.ids.input_semester.text = store.student_semester

    def submit_login(self):
        app = App.get_running_app()
        name = self.ids.input_name.text.strip() if 'input_name' in self.ids else ""
        career = self.ids.input_career.text.strip() if 'input_career' in self.ids else ""
        semester = self.ids.input_semester.text.strip() if 'input_semester' in self.ids else ""

        if not name:
            app.show_toast("Por favor ingresa tu nombre")
            return

        store = app.data_store
        store.student_name = name
        store.student_career = career
        store.student_semester = semester
        store.is_logged_in = True

        first_name = name.split()[0]
        app.show_toast(f"¡Bienvenido/a, {first_name}!")
        app.go_screen('home', clear_history=True)

    def skip_login(self):
        app = App.get_running_app()
        app.go_screen('home', clear_history=True)

    def go_back(self):
        app = App.get_running_app()
        app.go_back()
