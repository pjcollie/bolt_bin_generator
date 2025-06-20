from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.properties import StringProperty, ListProperty, NumericProperty

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text='Enter Your Name and Phone Number', font_size=30))
        self.name_input = TextInput(hint_text='Name', font_size=25, size_hint=(1, 0.3))
        self.phone_input = TextInput(hint_text='Phone', font_size=25, size_hint=(1, 0.3))
        next_btn = Button(text='Next', font_size=25, size_hint=(1, 0.3))
        next_btn.bind(on_press=self.go_to_bin_size)
        layout.add_widget(self.name_input)
        layout.add_widget(self.phone_input)
        layout.add_widget(next_btn)
        self.add_widget(layout)

    def go_to_bin_size(self, instance):
        app = App.get_running_app()
        app.name = self.name_input.text
        app.phone = self.phone_input.text
        if not app.name or not app.phone:
            self.name_input.hint_text = 'Name (Required)'
            self.phone_input.hint_text = 'Phone (Required)'
            return
        self.manager.current = 'bin_size'

class BinSizeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text='Choose Bin Size', font_size=30))
        btn_56 = Button(text='56 Holes', font_size=25, size_hint=(1, 0.4))
        btn_72 = Button(text='72 Holes', font_size=25, size_hint=(1, 0.4))
        btn_56.bind(on_press=lambda x: self.select_bin_size('56'))
        btn_72.bind(on_press=lambda x: self.select_bin_size('72'))
        layout.add_widget(btn_56)
        layout.add_widget(btn_72)
        self.add_widget(layout)

    def select_bin_size(self, size):
        app = App.get_running_app()
        app.bin_size = size
        app.max_rows = 7 if size == '56' else 9
        self.manager.current = 'material'

class MaterialScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text='Choose Material', font_size=30))
        for mat in App.get_running_app().materials:
            btn = Button(text=mat, font_size=25, size_hint=(1, 0.3))
            btn.bind(on_press=lambda x, m=mat: self.select_material(m))
            layout.add_widget(btn)
        self.add_widget(layout)

    def select_material(self, material):
        App.get_running_app().material = material
        self.manager.current = 'bin_config'

class BinConfigScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.layout.add_widget(Label(text='Configure Your Bin', font_size=30))
        self.diameter_list = BoxLayout(orientation='vertical', size_hint=(1, 0.6))
        self.layout.add_widget(self.diameter_list)
        add_btn = Button(text='Add Diameter', font_size=25, size_hint=(1, 0.2))
        finish_btn = Button(text='Finish', font_size=25, size_hint=(1, 0.2))
        add_btn.bind(on_press=self.add_diameter)
        finish_btn.bind(on_press=self.go_to_summary)  # Fixed binding
        self.layout.add_widget(add_btn)
        self.layout.add_widget(finish_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        self.update_diameter_list()

    def go_to_summary(self, instance):
        """Switch to the summary screen."""
        self.manager.current = 'summary'

    def add_diameter(self, instance):
        """Navigate to the add_diameter screen."""
        self.manager.current = 'add_diameter'

    def update_diameter_list(self):
        self.diameter_list.clear_widgets()
        app = App.get_running_app()
        for i, entry in enumerate(app.bin_data):
            lbl = Label(text=f"Diameter {entry['diameter']}: {', '.join(item for item in entry['items'] if item != 'Blank')}, {', '.join(entry['lengths'])}", font_size=20)
            self.diameter_list.add_widget(lbl)
        if len(app.bin_data) >= app.max_rows:
            self.layout.children[-2].disabled = True  # Disable 'Add Diameter' button

class AddDiameterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.layout.add_widget(Label(text='Add a Diameter', font_size=30))
        
        # Diameter selection
        self.diameter_spinner = Spinner(text='Select Diameter', values=App.get_running_app().diameters, font_size=25, size_hint=(1, 0.2))
        self.diameter_spinner.bind(text=self.on_diameter_change)
        self.layout.add_widget(self.diameter_spinner)
        
        # Items selection
        self.items_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.4))
        self.item_spinners = []
        for i in range(4):
            spinner = Spinner(text='Blank', values=App.get_running_app().item_options, font_size=20)
            self.item_spinners.append(spinner)
            self.items_layout.add_widget(spinner)
        self.layout.add_widget(self.items_layout)
        
        # Lengths selection
        self.lengths_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.4))
        self.length_checkboxes = {}
        self.selected_lengths = []
        self.layout.add_widget(self.lengths_layout)
        
        # Buttons
        save_btn = Button(text='Save Diameter', font_size=25, size_hint=(1, 0.2))
        save_btn.bind(on_press=self.save_diameter)
        self.layout.add_widget(save_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        self.update_lengths()

    def on_diameter_change(self, spinner, text):
        self.update_lengths()

    def update_lengths(self):
        self.lengths_layout.clear_widgets()
        self.length_checkboxes.clear()
        self.selected_lengths = []
        diameter = self.diameter_spinner.text if self.diameter_spinner.text != 'Select Diameter' else '1/4'
        lengths = App.get_running_app().available_lengths.get(diameter, [])
        for length in lengths:
            row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=50)
            cb = CheckBox(size_hint=(0.2, 1))
            cb.bind(active=self.on_checkbox_active)
            lbl = Label(text=length, font_size=20)
            row.add_widget(cb)
            row.add_widget(lbl)
            self.lengths_layout.add_widget(row)
            self.length_checkboxes[length] = cb

    def on_checkbox_active(self, checkbox, value):
        length = [lbl.text for row in self.lengths_layout.children for lbl in row.children if isinstance(lbl, Label)][list(self.length_checkboxes.values()).index(checkbox)]
        if value and length not in self.selected_lengths and len(self.selected_lengths) < 4:
            self.selected_lengths.append(length)
        elif not value and length in self.selected_lengths:
            self.selected_lengths.remove(length)
        elif value and len(self.selected_lengths) >= 4:
            checkbox.active = False

    def save_diameter(self, instance):
        app = App.get_running_app()
        if self.diameter_spinner.text == 'Select Diameter':
            return
        items = [spinner.text for spinner in reversed(self.item_spinners)]
        if len(set(items) - {'Blank'}) > 4:  # Limit non-blank items
            return
        if len(app.bin_data) >= app.max_rows:
            return
        app.bin_data.append({
            'diameter': self.diameter_spinner.text,
            'items': items,
            'lengths': sorted(self.selected_lengths, key=lambda x: float(x.replace('-', '.')))
        })
        self.diameter_spinner.text = 'Select Diameter'
        self.selected_lengths = []
        for spinner in self.item_spinners:
            spinner.text = 'Blank'
        self.manager.current = 'bin_config'

class SummaryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.layout.add_widget(Label(text='Your Bin Summary', font_size=30))
        self.summary_label = Label(text='', font_size=20, halign='left', valign='top')
        self.summary_label.bind(size=self.summary_label.setter('text_size'))  # Wrap text
        self.layout.add_widget(self.summary_label)
        done_btn = Button(text='Done', font_size=25, size_hint=(1, 0.2))
        done_btn.bind(on_press=lambda x: App.get_running_app().stop())
        self.layout.add_widget(done_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        app = App.get_running_app()
        summary = f"Name: {app.name}\nPhone: {app.phone}\nBin Size: {app.bin_size} holes\nMaterial: {app.material}\n\n"
        for entry in app.bin_data:
            items = ', '.join(item for item in entry['items'] if item != 'Blank')
            lengths = ', '.join(entry['lengths'])
            summary += f"Diameter {entry['diameter']}: {items or 'None'}, {lengths or 'None'}\n"
        self.summary_label.text = summary

class BoltBinApp(App):
    name = StringProperty('')
    phone = StringProperty('')
    bin_size = StringProperty('')
    material = StringProperty('')
    bin_data = ListProperty([])
    max_rows = NumericProperty(0)
    diameters = ListProperty(["1/4", "5/16", "3/8", "7/16", "1/2", "5/8", "3/4", "7/8", "1"])
    materials = ListProperty(["Grade 5 Zinc", "Stainless Steel", "Black Oxide"])
    available_lengths = {
        "1/4": ["3/8", "1/2", "3/4", "1", "1-1/4", "1-1/2", "2"],
        "5/16": ["1/2", "3/4", "1", "1-1/4", "1-1/2", "2", "2-1/2"],
        "3/8": ["1/2", "3/4", "1", "1-1/4", "1-1/2", "2", "2-1/2", "3"],
        "7/16": ["3/4", "1", "1-1/4", "1-1/2", "2", "2-1/2", "3"],
        "1/2": ["1", "1-1/4", "1-1/2", "2", "2-1/2", "3", "4"],
        "5/8": ["1", "1-1/2", "2", "2-1/2", "3", "4", "5"],
        "3/4": ["1", "1-1/2", "2", "2-1/2", "3", "4", "5", "6"],
        "7/8": ["1-1/2", "2", "2-1/2", "3", "4", "5", "6"],
        "1": ["2", "2-1/2", "3", "4", "5", "6", "8"]
    }
    item_options = ListProperty(["Nut", "Flatwasher", "Lockwasher", "Locknut", "Blank"])

    def build(self):
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(BinSizeScreen(name='bin_size'))
        sm.add_widget(MaterialScreen(name='material'))
        sm.add_widget(BinConfigScreen(name='bin_config'))
        sm.add_widget(AddDiameterScreen(name='add_diameter'))
        sm.add_widget(SummaryScreen(name='summary'))
        return sm

if __name__ == '__main__':
    BoltBinApp().run()