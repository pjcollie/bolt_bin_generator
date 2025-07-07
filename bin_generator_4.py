import json
import re
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.metrics import sp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line

# Configuration class to organize hardcoded data
class Config:
    DIAMETERS = ["1/4", "5/16", "3/8", "7/16", "1/2", "5/8", "3/4", "7/8", "1"]
    MATERIALS = ["Grade 5 Zinc", "Grade 5 Plain", "Grade 8 Yellow Zinc", "Grade 8 Plain", "Stainless Steel"]
    AVAILABLE_LENGTHS = {
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
    ITEM_OPTIONS = ["Nut", "Flatwasher", "Lockwasher", "Locknut", "Blank"]

# Custom button with better contrast
class ContrastButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.6, 0.8, 1)  # Blue background
        self.color = (1, 1, 1, 1)  # White text
        self.font_size = sp(30)

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text='Enter Your Name and Phone Number', font_size=sp(35), color=(0, 0, 0, 1)))
        self.name_input = TextInput(hint_text='Name', font_size=sp(30), size_hint=(1, 0.3), multiline=False, input_type='text')
        self.phone_input = TextInput(hint_text='Phone (10 digits)', font_size=sp(30), size_hint=(1, 0.3), multiline=False, input_type='number')
        next_btn = ContrastButton(text='Next', size_hint=(1, 0.3))
        next_btn.bind(on_press=self.go_to_bin_size)
        layout.add_widget(self.name_input)
        layout.add_widget(self.phone_input)
        layout.add_widget(next_btn)
        self.add_widget(layout)

    def on_enter(self):
        # Auto-focus name input to trigger keyboard
        self.name_input.focus = True

    def go_to_bin_size(self, instance):
        app = App.get_running_app()
        app.name = self.name_input.text.strip()
        app.phone = self.phone_input.text.strip()
        # Input validation for name and phone
        if not app.name or not re.match(r'^[A-Za-z\s]+$', app.name):
            popup = Popup(title='Error', content=Label(text='Name must contain only letters and spaces', font_size=sp(20)), size_hint=(0.5, 0.5))
            popup.open()
            return
        if not app.phone or not re.match(r'^\d{10}$', app.phone):
            popup = Popup(title='Error', content=Label(text='Phone must be 10 digits', font_size=sp(20)), size_hint=(0.5, 0.5))
            popup.open()
            return
        self.manager.current = 'bin_size'

class BinSizeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text='Choose Bin Size', font_size=sp(35), color=(0, 0, 0, 1)))
        btn_56 = ContrastButton(text='56 Holes', size_hint=(1, 0.4))
        btn_72 = ContrastButton(text='72 Holes', size_hint=(1, 0.4))
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.2))
        btn_56.bind(on_press=lambda x: self.select_bin_size('56'))
        btn_72.bind(on_press=lambda x: self.select_bin_size('72'))
        back_btn.bind(on_press=self.go_to_start)
        layout.add_widget(btn_56)
        layout.add_widget(btn_72)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def select_bin_size(self, size):
        app = App.get_running_app()
        app.bin_size = size
        app.max_rows = 7 if size == '56' else 9
        self.manager.current = 'material'

    def go_to_start(self, instance):
        self.manager.current = 'start'

class MaterialScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text='Choose Material', font_size=sp(35), color=(0, 0, 0, 1)))
        for mat in Config.MATERIALS:
            btn = ContrastButton(text=mat, size_hint=(1, 0.3))
            btn.bind(on_press=lambda x, m=mat: self.select_material(m))
            layout.add_widget(btn)
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.2))
        back_btn.bind(on_press=self.go_to_bin_size)
        layout.add_widget(back_btn)
        self.add_widget(layout)

    def select_material(self, material):
        App.get_running_app().material = material
        self.manager.current = 'bin_config'

    def go_to_bin_size(self, instance):
        self.manager.current = 'bin_size'

class BinConfigScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.layout.add_widget(Label(text='Configure Your Bin', font_size=sp(35), color=(0, 0, 0, 1)))
        self.diameter_list = BoxLayout(orientation='vertical', size_hint=(1, 0.6))
        self.layout.add_widget(self.diameter_list)
        self.add_btn = ContrastButton(text='Add Diameter', size_hint=(1, 0.2))
        finish_btn = ContrastButton(text='Finish', size_hint=(1, 0.2))
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.2))
        self.add_btn.bind(on_press=self.add_diameter)
        finish_btn.bind(on_press=self.go_to_summary)
        back_btn.bind(on_press=self.go_to_material)
        self.layout.add_widget(self.add_btn)
        self.layout.add_widget(finish_btn)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        self.update_diameter_list()

    def go_to_summary(self, instance):
        self.manager.current = 'summary'

    def go_to_material(self, instance):
        self.manager.current = 'material'

    def add_diameter(self, instance):
        app = App.get_running_app()
        if len(app.bin_data) >= app.max_rows:
            popup = Popup(title='Error', content=Label(text=f'Maximum {app.max_rows} diameters reached', font_size=sp(20)), size_hint=(0.5, 0.5))
            popup.open()
            return
        self.manager.current = 'add_diameter'

    def update_diameter_list(self):
        # Optimized widget reuse
        app = App.get_running_app()
        required_labels = len(app.bin_data)
        current_labels = len(self.diameter_list.children)
        # Add new labels if needed
        for i in range(current_labels, required_labels):
            self.diameter_list.add_widget(Label(font_size=sp(25), color=(0, 0, 0, 1)))
        # Update or remove existing labels
        for i, entry in enumerate(app.bin_data):
            if i < len(self.diameter_list.children):
                self.diameter_list.children[-(i+1)].text = f"Diameter {entry['diameter']}: {entry['lengths'][0] if entry['lengths'] else 'None'}"
        # Remove excess labels
        while len(self.diameter_list.children) > required_labels:
            self.diameter_list.remove_widget(self.diameter_list.children[0])
        # Disable add button if max rows reached
        self.add_btn.disabled = len(app.bin_data) >= app.max_rows

class AddDiameterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        with self.layout.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Light gray background
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # Preview section
        self.preview_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5))
        self.layout.add_widget(self.preview_layout)
        
        # Button section
        self.button_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.5))
        self.layout.add_widget(self.button_layout)
        
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.1))
        back_btn.bind(on_press=self.go_to_bin_config)
        self.button_layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_enter(self):
        app = App.get_running_app()
        self.preview_layout.clear_widgets()
        with self.preview_layout.canvas:
            Color(1, 1, 1, 1)  # White background for preview
            self.preview_rect = Rectangle(size=self.preview_layout.size, pos=self.preview_layout.pos)
        self.preview_layout.bind(size=self._update_preview_rect, pos=self._update_preview_rect)

        # Draw grid and labels
        max_rows = app.max_rows
        cell_width = self.preview_layout.width / 8  # 8 columns for simplicity
        cell_height = self.preview_layout.height / max_rows

        with self.preview_layout.canvas:
            Color(0, 0, 0, 1)  # Black lines
            for i in range(max_rows + 1):
                Line(points=[0, i * cell_height, self.preview_layout.width, i * cell_height])
            for i in range(9):  # 8 columns + 1 for border
                Line(points=[i * cell_width, 0, i * cell_width, self.preview_layout.height])

        # Label columns
        for i, diam in enumerate([''] + Config.DIAMETERS):
            lbl = Label(text=diam, size_hint=(None, 1), size=(cell_width, cell_height), pos=(i * cell_width, 0))
            self.preview_layout.add_widget(lbl)

        # Fill cells with data
        for i, entry in enumerate(app.bin_data):
            col = Config.DIAMETERS.index(entry['diameter']) + 1
            with self.preview_layout.canvas:
                Color(0, 0.5, 0, 0.5)  # Green fill for occupied cells
                Rectangle(pos=(col * cell_width, (max_rows - 1 - i) * cell_height), size=(cell_width, cell_height))
            lbl = Label(text=entry['lengths'][0] if entry['lengths'] else '', size_hint=(None, 1), size=(cell_width, cell_height), pos=(col * cell_width, (max_rows - 1 - i) * cell_height))
            self.preview_layout.add_widget(lbl)

        self.button_layout.clear_widgets()
        self.button_layout.add_widget(Label(text='Select Diameter', font_size=sp(35), color=(0, 0, 0, 1)))
        for diameter in Config.DIAMETERS:
            btn = ContrastButton(text=diameter, size_hint=(1, 0.1))
            btn.bind(on_press=lambda x, d=diameter: self.select_diameter(d))
            self.button_layout.add_widget(btn)
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.1))
        back_btn.bind(on_press=self.go_to_bin_config)
        self.button_layout.add_widget(back_btn)

    def _update_preview_rect(self, instance, value):
        self.preview_rect.pos = instance.pos
        self.preview_rect.size = instance.size

    def select_diameter(self, diameter):
        app = App.get_running_app()
        app.selected_diameter = diameter
        self.manager.current = 'add_length'

    def go_to_bin_config(self, instance):
        self.manager.current = 'bin_config'

class AddLengthScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        with self.layout.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Light gray background
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)
        self.layout.add_widget(Label(text='Select Length', font_size=sp(35), color=(0, 0, 0, 1)))
        self.lengths = []
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.1))
        back_btn.bind(on_press=self.go_to_add_diameter)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        app = App.get_running_app()
        self.layout.clear_widgets()
        with self.layout.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            self.rect = Rectangle(size=self.layout.size, pos=self.layout.pos)
        self.layout.bind(size=self._update_rect, pos=self._update_rect)
        self.layout.add_widget(Label(text='Select Length', font_size=sp(35), color=(0, 0, 0, 1)))
        self.lengths = Config.AVAILABLE_LENGTHS.get(app.selected_diameter, [])
        for length in self.lengths:
            btn = ContrastButton(text=length, size_hint=(1, 0.1))
            btn.bind(on_press=lambda x, l=length: self.select_length(l))
            self.layout.add_widget(btn)
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.1))
        back_btn.bind(on_press=self.go_to_add_diameter)
        self.layout.add_widget(back_btn)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def select_length(self, length):
        app = App.get_running_app()
        if len(app.bin_data) < app.max_rows:
            app.bin_data.append({
                'diameter': app.selected_diameter,
                'items': ['Blank'],  # Default to Blank item
                'lengths': [length]
            })
        self.manager.current = 'add_diameter'

    def go_to_add_diameter(self, instance):
        self.manager.current = 'add_diameter'

class SummaryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.layout.add_widget(Label(text='Your Bin Summary', font_size=sp(35), color=(0, 0, 0, 1)))
        self.summary_label = Label(text='', font_size=sp(25), halign='left', valign='top', color=(0, 0, 0, 1))
        self.summary_label.bind(size=self.summary_label.setter('text_size'))
        self.layout.add_widget(self.summary_label)
        save_btn = ContrastButton(text='Save to File', size_hint=(1, 0.2))
        done_btn = ContrastButton(text='Done', size_hint=(1, 0.2))
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.2))
        save_btn.bind(on_press=self.save_to_file)
        done_btn.bind(on_press=lambda x: App.get_running_app().stop())
        back_btn.bind(on_press=self.go_to_bin_config)
        self.layout.add_widget(save_btn)
        self.layout.add_widget(done_btn)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        app = App.get_running_app()
        summary = f"Name: {app.name}\nPhone: {app.phone}\nBin Size: {app.bin_size} holes\nMaterial: {app.material}\n\n"
        for entry in app.bin_data:
            items = ', '.join(item for item in entry['items'] if item != 'Blank')
            lengths = ', '.join(entry['lengths'])
            summary += f"Diameter {entry['diameter']}: {items or 'None'}, {lengths or 'None'}\n"
        self.summary_label.text = summary

    def save_to_file(self, instance):
        app = App.get_running_app()
        data = {
            'name': app.name,
            'phone': app.phone,
            'bin_size': app.bin_size,
            'material': app.material,
            'bin_data': app.bin_data
        }
        try:
            with open('bin_config.json', 'w') as f:
                json.dump(data, f, indent=4)
            popup = Popup(title='Success', content=Label(text='Configuration saved to bin_config.json', font_size=sp(20)), size_hint=(0.5, 0.5))
            popup.open()
        except Exception as e:
            popup = Popup(title='Error', content=Label(text=f'Failed to save: {str(e)}', font_size=sp(20)), size_hint=(0.5, 0.5))
            popup.open()

    def go_to_bin_config(self, instance):
        self.manager.current = 'bin_config'

class BoltBinApp(App):
    name = StringProperty('')
    phone = StringProperty('')
    bin_size = StringProperty('')
    material = StringProperty('')
    bin_data = ListProperty([])
    max_rows = NumericProperty(0)
    diameters = ListProperty(Config.DIAMETERS)
    materials = ListProperty(Config.MATERIALS)
    available_lengths = Config.AVAILABLE_LENGTHS
    item_options = ListProperty(Config.ITEM_OPTIONS)
    selected_diameter = StringProperty('')

    def build(self):
        # Maximize window for full screen
        Window.maximize()
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(BinSizeScreen(name='bin_size'))
        sm.add_widget(MaterialScreen(name='material'))
        sm.add_widget(BinConfigScreen(name='bin_config'))
        sm.add_widget(AddDiameterScreen(name='add_diameter'))
        sm.add_widget(AddLengthScreen(name='add_length'))
        sm.add_widget(SummaryScreen(name='summary'))
        return sm

if __name__ == '__main__':
    BoltBinApp().run()
