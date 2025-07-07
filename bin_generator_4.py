import json
import re
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.metrics import sp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.config import Config

# Configure Kivy for macOS Retina displays and performance
Config.set('graphics', 'multisamples', '0')  # Disable multisampling
Config.set('graphics', 'kivy_clock', 'free_all')  # Optimize clock
Config.set('graphics', 'dpi', 'auto')  # Auto-detect DPI for Retina displays

# Configuration class to organize hardcoded data
class Config:
    DIAMETERS = ["1/4", "5/16", "3/8", "7/16", "1/2", "5/8", "3/4", "7/8", "1"]
    MATERIALS = ["Grade 5 Zinc", "Grade 5 Plain", "Grade 8 Yellow Zinc", "Grade 8 Plain", "Stainless Steel"]
    AVAILABLE_LENGTHS = {
        "1/4": ["3/8", "1/2", "3/4", "1", "1-1/4", "1-1/2", "2", "2-1/4", "2-1/2", "2-3/4", "3", "3-1/2"],
        "5/16": ["1/2", "3/4", "1", "1-1/4", "1-1/2", "2", "2-1/2", "2-3/4", "3", "3-1/4", "3-1/2", "4"],
        "3/8": ["1/2", "3/4", "1", "1-1/4", "1-1/2", "2", "2-1/2", "3", "3-1/2", "4", "4-1/2", "5"],
        "7/16": ["3/4", "1", "1-1/4", "1-1/2", "2", "2-1/2", "3", "3-1/2", "4", "4-1/2", "5", "5-1/2"],
        "1/2": ["1", "1-1/4", "1-1/2", "2", "2-1/2", "3", "4", "4-1/2", "5", "5-1/2", "6", "6-1/2"],
        "5/8": ["1", "1-1/2", "2", "2-1/2", "3", "4", "5", "5-1/2", "6", "6-1/2", "7", "7-1/2"],
        "3/4": ["1", "1-1/2", "2", "2-1/2", "3", "4", "5", "6", "6-1/2", "7", "7-1/2", "8"],
        "7/8": ["1-1/2", "2", "2-1/2", "3", "4", "5", "6", "6-1/2", "7", "7-1/2", "8", "8-1/2"],
        "1": ["2", "2-1/2", "3", "4", "5", "6", "8", "8-1/2", "9", "9-1/2", "10", "10-1/2"]
    }
    ITEM_OPTIONS = ["Nut", "Flatwasher", "Lockwasher", "Nylon Locknut"]

# Custom button with better contrast
class ContrastButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.2, 0.6, 0.8, 1)  # Blue background
        self.color = (1, 1, 1, 1)  # White text
        self.font_size = sp(20)

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=sp(20), spacing=sp(20), size_hint=(1, 1))
        self.layout.add_widget(Label(text='Enter Your Name and Phone Number', font_size=sp(35), color=(0, 0, 0, 1), size_hint_y=0.2))
        self.name_input = TextInput(hint_text='Name', font_size=sp(30), size_hint=(1, 0.3), multiline=False, input_type='text')
        self.phone_input = TextInput(hint_text='Phone (10 digits)', font_size=sp(30), size_hint=(1, 0.3), multiline=False, input_type='number')
        next_btn = ContrastButton(text='Next', size_hint=(1, 0.2))
        next_btn.bind(on_press=self.go_to_bin_size)
        self.layout.add_widget(self.name_input)
        self.layout.add_widget(self.phone_input)
        self.layout.add_widget(next_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        self.name_input.focus = True

    def go_to_bin_size(self, instance):
        app = App.get_running_app()
        app.name = self.name_input.text.strip()
        app.phone = self.phone_input.text.strip()
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
        self.layout = BoxLayout(orientation='vertical', padding=sp(20), spacing=sp(20), size_hint=(1, 1))
        self.layout.add_widget(Label(text='Choose Bin Size', font_size=sp(35), color=(0, 0, 0, 1), size_hint_y=0.2))
        btn_56 = ContrastButton(text='56 Holes', size_hint=(1, 0.3))
        btn_72 = ContrastButton(text='72 Holes', size_hint=(1, 0.3))
        btn_56.bind(on_press=lambda x: self.select_bin_size('56'))
        btn_72.bind(on_press=lambda x: self.select_bin_size('72'))
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.2))
        back_btn.bind(on_press=self.go_to_start)
        self.layout.add_widget(btn_56)
        self.layout.add_widget(btn_72)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

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
        self.layout = BoxLayout(orientation='vertical', padding=sp(20), spacing=sp(20), size_hint=(1, 1))
        self.scroll_view = ScrollView(size_hint=(1, 0.8))
        self.material_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.material_list.bind(minimum_height=self.material_list.setter('height'))
        for mat in Config.MATERIALS:
            btn = ContrastButton(text=mat, size_hint=(1, None), height=sp(60))
            btn.bind(on_press=lambda x, m=mat: self.select_material(m))
            self.material_list.add_widget(btn)
        self.scroll_view.add_widget(self.material_list)
        self.layout.add_widget(Label(text='Choose Material', font_size=sp(35), color=(0, 0, 0, 1), size_hint_y=0.1))
        self.layout.add_widget(self.scroll_view)
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.1))
        back_btn.bind(on_press=self.go_to_bin_size)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def select_material(self, material):
        App.get_running_app().material = material
        self.manager.current = 'bin_config'

    def go_to_bin_size(self, instance):
        self.manager.current = 'bin_size'

class BinConfigScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=sp(20), spacing=sp(20), size_hint=(1, 1))
        self.scroll_view = ScrollView(size_hint=(1, 0.6))
        self.diameter_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.diameter_list.bind(minimum_height=self.diameter_list.setter('height'))
        self.scroll_view.add_widget(self.diameter_list)
        self.layout.add_widget(Label(text='Configure Your Bin', font_size=sp(35), color=(0, 0, 0, 1), size_hint_y=0.2))
        self.layout.add_widget(self.scroll_view)
        self.add_btn = ContrastButton(text='Add Diameter', size_hint=(1, 0.1))
        finish_btn = ContrastButton(text='Finish', size_hint=(1, 0.1))
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.1))
        self.add_btn.bind(on_press=self.add_diameter)
        finish_btn.bind(on_press=self.go_to_summary)
        back_btn.bind(on_press=self.go_to_material)
        self.layout.add_widget(self.add_btn)
        self.layout.add_widget(finish_btn)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def on_enter(self):
        self.update_diameter_list()

    def update_diameter_list(self):
        app = App.get_running_app()
        required_labels = len(app.bin_data)
        current_labels = len(self.diameter_list.children)
        for i in range(current_labels, required_labels):
            self.diameter_list.add_widget(Label(font_size=sp(25), color=(0, 0, 0, 1), size_hint_y=None, height=sp(40)))
        for i, entry in enumerate(app.bin_data):
            lengths_text = ', '.join(entry['lengths']) if entry['lengths'] else 'No lengths'
            items_text = ', '.join(entry['items']) if entry['items'] else 'No items'
            self.diameter_list.children[-(i+1)].text = f"Diameter {entry['diameter']}: {lengths_text}, {items_text}"
        while len(self.diameter_list.children) > required_labels:
            self.diameter_list.remove_widget(self.diameter_list.children[0])
        self.add_btn.disabled = len(app.bin_data) >= app.max_rows

    def add_diameter(self, instance):
        app = App.get_running_app()
        if len(app.bin_data) >= app.max_rows:
            popup = Popup(title='Error', content=Label(text=f'Maximum {app.max_rows} diameters reached', font_size=sp(20)), size_hint=(0.5, 0.5))
            popup.open()
            return
        self.manager.current = 'add_diameter'

    def go_to_summary(self, instance):
        self.manager.current = 'summary'

    def go_to_material(self, instance):
        self.manager.current = 'material'

class AddDiameterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=sp(20), spacing=sp(20), size_hint=(1, 1))
        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Light gray background
            self.rect = Rectangle(size=Window.size, pos=(0, 0))
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Diameter selection section
        self.diameter_selection = BoxLayout(orientation='vertical', size_hint_y=0.5)
        self.diameter_selection.add_widget(Label(text='Select Diameter', font_size=sp(35), color=(0, 0, 0, 1), size_hint_y=0.2))
        self.diameter_grid = GridLayout(cols=3, rows=3, size_hint_y=0.8)
        for diameter in Config.DIAMETERS:
            btn = ContrastButton(text=diameter, size_hint=(1, None), height=sp(60))
            btn.bind(on_press=lambda x, d=diameter: self.select_diameter(d))
            self.diameter_grid.add_widget(btn)
        self.diameter_selection.add_widget(self.diameter_grid)
        self.layout.add_widget(self.diameter_selection)

        # Preview section
        self.preview_layout = FloatLayout(size_hint_y=0.4)
        self.layout.add_widget(self.preview_layout)

        # Back button
        back_btn = ContrastButton(text='Back', size_hint_y=0.1)
        back_btn.bind(on_press=self.go_to_bin_config)
        self.layout.add_widget(back_btn)

        self.add_widget(self.layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_enter(self):
        app = App.get_running_app()
        self.preview_layout.clear_widgets()
        self.preview_layout.canvas.clear()

        # Set white background for the preview
        with self.preview_layout.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.preview_rect = Rectangle(size=self.preview_layout.size, pos=self.preview_layout.pos)

        self.preview_layout.bind(size=self._update_preview_rect, pos=self._update_preview_rect)

        # Only draw the grid and labels if there are items in bin_data
        if app.bin_data:
            max_rows = app.max_rows
            num_cols = 9  # 1 for diameter label, 8 for items
            cell_width = self.preview_layout.width / num_cols
            cell_height = self.preview_layout.height / max_rows

            # Draw grid lines
            with self.preview_layout.canvas:
                Color(0, 0, 0, 1)  # Black lines
                for i in range(max_rows + 1):
                    Line(points=[0, i * cell_height, self.preview_layout.width, i * cell_height])
                for i in range(num_cols + 1):
                    Line(points=[i * cell_width, 0, i * cell_width, self.preview_layout.height])

            # Populate the grid with diameters and items
            for row in range(max_rows):
                if row < len(app.bin_data):
                    entry = app.bin_data[row]
                    diameter = entry['diameter']
                    # Combine lengths and items in the order they were selected
                    selected_items = entry['lengths'] + entry['items']

                    # Add diameter label in the first column
                    diameter_label = Label(
                        text=diameter,
                        size_hint=(None, None),
                        size=(cell_width, cell_height),
                        pos=(0, (max_rows - 1 - row) * cell_height),
                        color=(0, 0, 0, 1)
                    )
                    self.preview_layout.add_widget(diameter_label)

                    # Add selected items from left to right (up to 8 items)
                    for col in range(1, num_cols):
                        if col - 1 < len(selected_items):
                            item = selected_items[col - 1]
                            item_label = Label(
                                text=item,
                                size_hint=(None, None),
                                size=(cell_width, cell_height),
                                pos=(col * cell_width, (max_rows - 1 - row) * cell_height),
                                color=(0, 0, 0, 1)
                            )
                            self.preview_layout.add_widget(item_label)

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
        self.layout = BoxLayout(orientation='vertical', padding=sp(20), spacing=sp(20), size_hint=(1, 1))
        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Light gray background
            self.rect = Rectangle(size=Window.size, pos=(0, 0))
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.label = Label(text='', font_size=sp(35), color=(0, 0, 0, 1), size_hint_y=0.1)
        self.grid = GridLayout(cols=4, rows=4, size_hint_y=0.7, spacing=sp(10), padding=sp(10))
        self.button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2)
        self.confirm_btn = ContrastButton(text='Confirm')
        self.back_btn = ContrastButton(text='Back')
        self.button_layout.add_widget(self.confirm_btn)
        self.button_layout.add_widget(self.back_btn)
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.grid)
        self.layout.add_widget(self.button_layout)
        self.add_widget(self.layout)
        self.selected_lengths = set()
        self.selected_items = set()

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_enter(self):
        app = App.get_running_app()
        diameter = app.selected_diameter
        self.label.text = f"Select Lengths and Items for Diameter {diameter}"
        available_lengths = Config.AVAILABLE_LENGTHS.get(diameter, [])
        self.grid.clear_widgets()
        self.length_buttons = {}
        self.item_buttons = {}

        # Populate grid with all available lengths (up to 12)
        for i in range(12):
            if i < len(available_lengths):
                length = available_lengths[i]
                btn = ContrastButton(text=length, size_hint=(1, None), height=sp(60))
                btn.bind(on_press=lambda x, l=length: self.toggle_selection(x, l, 'length'))
                self.length_buttons[btn] = length
                if length in self.selected_lengths:
                    btn.text = f"{length} [X]"
                self.grid.add_widget(btn)
            else:
                btn = Button(text='', disabled=True, size_hint=(1, None), height=sp(60))
                self.grid.add_widget(btn)

        # Bottom row for items
        for i, item in enumerate(Config.ITEM_OPTIONS):
            btn = ContrastButton(text=item, size_hint=(1, None), height=sp(60))
            btn.bind(on_press=lambda x, it=item: self.toggle_selection(x, it, 'item'))
            self.item_buttons[btn] = item
            if item in self.selected_items:
                btn.text = f"{item} [X]"
            self.grid.add_widget(btn)

        self.confirm_btn.bind(on_press=self.confirm_selection)
        self.back_btn.bind(on_press=self.go_to_add_diameter)

    def toggle_selection(self, instance, value, type_):
        if type_ == 'length':
            target_set = self.selected_lengths
            button_dict = self.length_buttons
        else:
            target_set = self.selected_items
            button_dict = self.item_buttons

        if value in target_set:
            target_set.remove(value)
            instance.text = value
        else:
            target_set.add(value)
            instance.text = f"{value} [X]"

    def confirm_selection(self, instance):
        app = App.get_running_app()
        diameter = app.selected_diameter
        for entry in app.bin_data:
            if entry['diameter'] == diameter:
                entry['lengths'] = list(set(entry['lengths'] + list(self.selected_lengths)))
                entry['items'] = list(set(entry['items'] + list(self.selected_items)))
                break
        else:
            app.bin_data.append({
                'diameter': diameter,
                'lengths': list(self.selected_lengths),
                'items': list(self.selected_items)
            })
        self.selected_lengths.clear()
        self.selected_items.clear()
        self.manager.current = 'bin_config'

    def go_to_add_diameter(self, instance):
        self.manager.current = 'add_diameter'

class SummaryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=sp(20), spacing=sp(20), size_hint=(1, 1))
        self.layout.add_widget(Label(text='Your Bin Summary', font_size=sp(35), color=(0, 0, 0, 1), size_hint_y=0.1))
        self.summary_label = Label(text='', font_size=sp(25), halign='left', valign='top', color=(0, 0, 0, 1), size_hint_y=0.6)
        self.summary_label.bind(size=self.summary_label.setter('text_size'))
        self.layout.add_widget(self.summary_label)
        save_btn = ContrastButton(text='Save to File', size_hint=(1, 0.1))
        done_btn = ContrastButton(text='Done', size_hint=(1, 0.1))
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.1))
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
            items = ', '.join(entry['items']) if entry['items'] else 'None'
            lengths = ', '.join(entry['lengths']) if entry['lengths'] else 'None'
            summary += f"Diameter {entry['diameter']}: Items - {items}, Lengths - {lengths}\n"
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
