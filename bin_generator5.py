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
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Black background
            self.rect = Rectangle(size=Window.size, pos=(0, 0))
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.layout.add_widget(Label(text='Enter Your Name and Phone Number', font_size=sp(35), color=(1, 1, 1, 1), size_hint_y=0.2))
        self.name_input = TextInput(hint_text='Name', font_size=sp(30), size_hint=(1, 0.3), multiline=False, input_type='text', foreground_color=(1, 1, 1, 1), background_color=(0, 0, 0, 1))
        self.phone_input = TextInput(hint_text='Phone (10 digits)', font_size=sp(30), size_hint=(1, 0.3), multiline=False, input_type='number', foreground_color=(1, 1, 1, 1), background_color=(0, 0, 0, 1))
        next_btn = ContrastButton(text='Next', size_hint=(1, 0.2))
        next_btn.bind(on_press=self.go_to_bin_size)
        self.layout.add_widget(self.name_input)
        self.layout.add_widget(self.phone_input)
        self.layout.add_widget(next_btn)
        self.add_widget(self.layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_enter(self):
        self.name_input.focus = True

    def go_to_bin_size(self, instance):
        app = App.get_running_app()
        app.name = self.name_input.text.strip()
        app.phone = self.phone_input.text.strip()
        if not app.name or not re.match(r'^[A-Za-z\s]+$', app.name):
            popup = Popup(title='Error', content=Label(text='Name must contain only letters and spaces', font_size=sp(20), color=(1, 1, 1, 1)), size_hint=(0.5, 0.5), background_color=(0, 0, 0, 1))
            popup.open()
            return
        if not app.phone or not re.match(r'^\d{10}$', app.phone):
            popup = Popup(title='Error', content=Label(text='Phone must be 10 digits', font_size=sp(20), color=(1, 1, 1, 1)), size_hint=(0.5, 0.5), background_color=(0, 0, 0, 1))
            popup.open()
            return
        self.manager.current = 'bin_size'

class BinSizeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=sp(20), spacing=sp(20), size_hint=(1, 1))
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Black background
            self.rect = Rectangle(size=Window.size, pos=(0, 0))
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.layout.add_widget(Label(text='Choose Bin Size', font_size=sp(35), color=(1, 1, 1, 1), size_hint_y=0.2))
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

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

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
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Black background
            self.rect = Rectangle(size=Window.size, pos=(0, 0))
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.scroll_view = ScrollView(size_hint=(1, 0.8))
        self.material_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.material_list.bind(minimum_height=self.material_list.setter('height'))
        for mat in Config.MATERIALS:
            btn = ContrastButton(text=mat, size_hint=(1, None), height=sp(60))
            btn.bind(on_press=lambda x, m=mat: self.select_material(m))
            self.material_list.add_widget(btn)
        self.scroll_view.add_widget(self.material_list)
        self.layout.add_widget(Label(text='Choose Material', font_size=sp(35), color=(1, 1, 1, 1), size_hint_y=0.1))
        self.layout.add_widget(self.scroll_view)
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.1))
        back_btn.bind(on_press=self.go_to_bin_size)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def select_material(self, material):
        App.get_running_app().material = material
        self.manager.current = 'bin_config'

    def go_to_bin_size(self, instance):
        self.manager.current = 'bin_size'

class BinConfigScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=sp(20), spacing=sp(20), size_hint=(1, 1))
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Black background
            self.rect = Rectangle(size=Window.size, pos=(0, 0))
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.scroll_view = ScrollView(size_hint=(1, 0.92))  # Increased size_hint_y to 0.92
        self.bin_layout = FloatLayout(size_hint_y=None)
        self.scroll_view.add_widget(self.bin_layout)
        self.layout.add_widget(Label(text='Configure Your Bin', font_size=sp(35), color=(1, 1, 1, 1), size_hint_y=0.03))  # Reduced size_hint_y
        self.layout.add_widget(self.scroll_view)
        self.add_btn = ContrastButton(text='Add Diameter', size_hint=(1, 0.05))  # Increased size_hint_y
        finish_btn = ContrastButton(text='Finish', size_hint=(1, 0.05))  # Increased size_hint_y
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.05))  # Increased size_hint_y
        self.add_btn.bind(on_press=self.add_diameter)
        finish_btn.bind(on_press=self.go_to_summary)
        back_btn.bind(on_press=self.go_to_material)
        self.layout.add_widget(self.add_btn)
        self.layout.add_widget(finish_btn)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_enter(self):
        app = App.get_running_app()
        self.bin_layout.clear_widgets()
        self.bin_layout.canvas.clear()

        if app.bin_data:
            max_rows = app.max_rows
            num_cols = 8  # 8 columns per row
            layout_width = self.bin_layout.width * 0.99  # Increased width to 99%
            layout_height = max_rows * sp(80)  # Increased height per row
            layout_x = (self.bin_layout.width - layout_width) / 2
            layout_y = (self.bin_layout.height - layout_height) / 2

            with self.bin_layout.canvas.before:
                Color(1, 1, 1, 1)  # White background
                self.bin_rect = Rectangle(size=(layout_width, layout_height), pos=(layout_x, layout_y))

            self.bin_layout.bind(size=self._update_bin_rect, pos=self._update_bin_rect)

            cell_width = layout_width / num_cols
            cell_height = layout_height / max_rows

            with self.bin_layout.canvas:
                Color(0, 0, 0, 1)  # Black lines
                for i in range(max_rows + 1):
                    Line(points=[layout_x, layout_y + i * cell_height, layout_x + layout_width, layout_y + i * cell_height])
                for i in range(num_cols + 1):
                    Line(points=[layout_x + i * cell_width, layout_y, layout_x + i * cell_width, layout_y + layout_height])

            for row in range(max_rows):
                if row < len(app.bin_data):
                    entry = app.bin_data[row]
                    diameter = entry['diameter']
                    selected_items = entry['lengths'] + entry['items']
                    for col in range(num_cols):
                        if col < len(selected_items):
                            item_or_length = selected_items[col]
                            size_text = f"{diameter} x {item_or_length}"
                            item_label = Label(
                                text=size_text,
                                size_hint=(None, None),
                                size=(cell_width, cell_height),
                                pos=(layout_x + col * cell_width, layout_y + (max_rows - 1 - row) * cell_height),
                                color=(0, 0, 0, 1)
                            )
                            self.bin_layout.add_widget(item_label)

    def _update_bin_rect(self, instance, value):
        layout_width = instance.width * 0.99  # Increased width
        layout_height = app.max_rows * sp(80)  # Increased height
        layout_x = (instance.width - layout_width) / 2
        layout_y = (instance.height - layout_height) / 2
        self.bin_rect.pos = (layout_x, layout_y)
        self.bin_rect.size = (layout_width, layout_height)

    def add_diameter(self, instance):
        app = App.get_running_app()
        if len(app.bin_data) >= app.max_rows:
            popup = Popup(title='Error', content=Label(text=f'Maximum {app.max_rows} diameters reached', font_size=sp(20), color=(1, 1, 1, 1)), size_hint=(0.5, 0.5), background_color=(0, 0, 0, 1))
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
            Color(0, 0, 0, 1)  # Black background
            self.rect = Rectangle(size=Window.size, pos=(0, 0))
        self.bind(size=self._update_rect, pos=self._update_rect)

        # Diameter selection section
        self.diameter_selection = BoxLayout(orientation='vertical', size_hint_y=0.3)
        self.diameter_selection.add_widget(Label(text='Select Diameter', font_size=sp(35), color=(1, 1, 1, 1), size_hint_y=0.2))
        self.diameter_grid = GridLayout(cols=3, rows=3, size_hint_y=0.8)
        for diameter in Config.DIAMETERS:
            btn = ContrastButton(text=diameter, size_hint=(1, None), height=sp(60))
            btn.bind(on_press=lambda x, d=diameter: self.select_diameter(d))
            self.diameter_grid.add_widget(btn)
        self.diameter_selection.add_widget(self.diameter_grid)
        self.layout.add_widget(self.diameter_selection)

        # Preview section
        self.preview_layout = FloatLayout(size_hint_y=0.6)
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

        # Set white background for the preview and center it with higher positioning
        preview_width = self.preview_layout.width * 0.8
        preview_height = self.preview_layout.height * 0.9  # Increased height
        preview_x = (self.preview_layout.width - preview_width) / 2
        preview_y = (self.preview_layout.height - preview_height) / 2 + self.layout.height * 0.15  # Shift up further
        with self.preview_layout.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.preview_rect = Rectangle(size=(preview_width, preview_height), pos=(preview_x, preview_y))

        self.preview_layout.bind(size=self._update_preview_rect, pos=self._update_preview_rect)

        # Draw the grid and labels if there are items in bin_data
        if app.bin_data:
            max_rows = app.max_rows
            num_cols = 8  # 8 columns
            cell_width = preview_width / num_cols
            cell_height = preview_height / max_rows

            # Draw grid lines
            with self.preview_layout.canvas:
                Color(0, 0, 0, 1)  # Black lines
                for i in range(max_rows + 1):
                    Line(points=[preview_x, preview_y + i * cell_height, preview_x + preview_width, preview_y + i * cell_height])
                for i in range(num_cols + 1):
                    Line(points=[preview_x + i * cell_width, preview_y, preview_x + i * cell_width, preview_y + preview_height])

            # Populate the grid with sizes (diameter x length/item) starting from the first column
            for row in range(max_rows):
                if row < len(app.bin_data):
                    entry = app.bin_data[row]
                    diameter = entry['diameter']
                    selected_items = entry['lengths'] + entry['items']

                    # Add sizes across 8 columns
                    for col in range(num_cols):
                        if col < len(selected_items):
                            item_or_length = selected_items[col]
                            size_text = f"{diameter} x {item_or_length}"
                            item_label = Label(
                                text=size_text,
                                size_hint=(None, None),
                                size=(cell_width, cell_height),
                                pos=(preview_x + col * cell_width, preview_y + (max_rows - 1 - row) * cell_height),
                                color=(0, 0, 0, 1)
                            )
                            self.preview_layout.add_widget(item_label)

    def _update_preview_rect(self, instance, value):
        preview_width = instance.width * 0.8
        preview_height = instance.height * 0.9  # Increased height
        preview_x = (instance.width - preview_width) / 2
        preview_y = (instance.height - preview_height) / 2 + self.layout.height * 0.15  # Shift up further
        self.preview_rect.pos = (preview_x, preview_y)
        self.preview_rect.size = (preview_width, preview_height)

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
            Color(0, 0, 0, 1)  # Black background
            self.rect = Rectangle(size=Window.size, pos=(0, 0))
        self.bind(size=self._update_rect, pos=self._update_rect)

        self.label = Label(text='', font_size=sp(35), color=(1, 1, 1, 1), size_hint_y=0.1)
        self.grid = GridLayout(cols=4, rows=4, size_hint_y=0.5, spacing=sp(10), padding=sp(10))
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
        with self.canvas.before:
            Color(0, 0, 0, 1)  # Black background
            self.rect = Rectangle(size=Window.size, pos=(0, 0))
        self.bind(size=self._update_rect, pos=self._update_rect)
        self.summary_layout = FloatLayout(size_hint_y=0.95)  # Increased size_hint_y to 0.95
        self.layout.add_widget(self.summary_layout)
        save_btn = ContrastButton(text='Save to File', size_hint=(1, 0.02))  # Reduced size_hint_y
        done_btn = ContrastButton(text='Done', size_hint=(1, 0.02))  # Reduced size_hint_y
        back_btn = ContrastButton(text='Back', size_hint=(1, 0.02))  # Reduced size_hint_y
        save_btn.bind(on_press=self.save_to_file)
        done_btn.bind(on_press=lambda x: App.get_running_app().stop())
        back_btn.bind(on_press=self.go_to_bin_config)
        self.layout.add_widget(save_btn)
        self.layout.add_widget(done_btn)
        self.layout.add_widget(back_btn)
        self.add_widget(self.layout)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_enter(self):
        app = App.get_running_app()
        self.summary_layout.clear_widgets()
        self.summary_layout.canvas.clear()

        if app.bin_data:
            max_rows = app.max_rows
            num_cols = 8  # 8 columns per row
            layout_width = self.summary_layout.width * 0.95  # Increased width
            layout_height = max_rows * sp(60)  # Increased height per row
            layout_x = (self.summary_layout.width - layout_width) / 2
            layout_y = (self.summary_layout.height - layout_height) / 2 + sp(50)  # Shift up

            with self.summary_layout.canvas.before:
                Color(1, 1, 1, 1)  # White background
                self.summary_rect = Rectangle(size=(layout_width, layout_height), pos=(layout_x, layout_y))

            self.summary_layout.bind(size=self._update_summary_rect, pos=self._update_summary_rect)

            cell_width = layout_width / num_cols
            cell_height = layout_height / max_rows

            with self.summary_layout.canvas:
                Color(0, 0, 0, 1)  # Black lines
                for i in range(max_rows + 1):
                    Line(points=[layout_x, layout_y + i * cell_height, layout_x + layout_width, layout_y + i * cell_height])
                for i in range(num_cols + 1):
                    Line(points=[layout_x + i * cell_width, layout_y, layout_x + i * cell_width, layout_y + layout_height])

            for row in range(max_rows):
                if row < len(app.bin_data):
                    entry = app.bin_data[row]
                    diameter = entry['diameter']
                    selected_items = entry['lengths'] + entry['items']
                    for col in range(num_cols):
                        if col < len(selected_items):
                            item_or_length = selected_items[col]
                            size_text = f"{diameter} x {item_or_length}"
                            item_label = Label(
                                text=size_text,
                                size_hint=(None, None),
                                size=(cell_width, cell_height),
                                pos=(layout_x + col * cell_width, layout_y + (max_rows - 1 - row) * cell_height),
                                color=(0, 0, 0, 1)
                            )
                            self.summary_layout.add_widget(item_label)

    def _update_summary_rect(self, instance, value):
        layout_width = instance.width * 0.95  # Increased width
        layout_height = app.max_rows * sp(60)  # Increased height
        layout_x = (instance.width - layout_width) / 2
        layout_y = (instance.height - layout_height) / 2 + sp(50)  # Shift up
        self.summary_rect.pos = (layout_x, layout_y)
        self.summary_rect.size = (layout_width, layout_height)

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
            popup = Popup(title='Success', content=Label(text='Configuration saved to bin_config.json', font_size=sp(20), color=(1, 1, 1, 1)), size_hint=(0.5, 0.5), background_color=(0, 0, 0, 1))
            popup.open()
        except Exception as e:
            popup = Popup(title='Error', content=Label(text=f'Failed to save: {str(e)}', font_size=sp(20), color=(1, 1, 1, 1)), size_hint=(0.5, 0.5), background_color=(0, 0, 0, 1))
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
