import gi
import base64
import sys
import random
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from cryptography.fernet import Fernet
import hashlib

def AddEntry(label, password):
    toadd = label
    toadd += "\\%%"
    toadd += password
    toadd = encrypt(toadd, masterpass)
    with open(filepath, "a") as file:
        file.write("\n" + toadd)
def get_fernet_key(key):
    # Derive a Fernet key from the user key (masterpass)
    digest = hashlib.sha256(key.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest)

def encrypt(string, key):
    # --- Original "spaghetti" encryption ---
    encrypted_str = ""
    salt_insert_index = 0
    current_index = 0
    output = ""
    input_str = string
    salt = str(key.encode('utf-8'))[2:-1]
    b64_encoded = str(base64.b64encode(input_str.encode('utf-8')))
    while salt_insert_index < 1:
        salt_insert_index = random.randint(2, len(b64_encoded) - 1)
    while not current_index - 1 == salt_insert_index:
        output += b64_encoded[current_index]
        current_index += 1
    output += salt
    total_length = len(b64_encoded) + len(salt)
    while not len(output) == total_length:
        output += b64_encoded[current_index]
        current_index += 1
    spaghetti_encrypted = str(base64.b64encode(output.encode('utf-8')))[2:-1]

    # --- Secure Fernet encryption of the spaghetti-encrypted string ---
    fernet = Fernet(get_fernet_key(key))
    fernet_encrypted = fernet.encrypt(spaghetti_encrypted.encode('utf-8')).decode('utf-8')

    # Return only the Fernet-encrypted spaghetti-encrypted string
    return fernet_encrypted

def decrypt(string, key):
    # Try Fernet decryption first (should always be Fernet-encrypted spaghetti)
    try:
        fernet = Fernet(get_fernet_key(key))
        spaghetti_encrypted = fernet.decrypt(string.encode('utf-8')).decode('utf-8')
    except Exception:
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text="Invalid key or invalid string.",
        )
        dialog.format_secondary_text("The provided key or string is invalid. The application will now exit.")
        dialog.run()
        dialog.destroy()
        Gtk.main_quit()

    # --- Original "spaghetti" decryption ---
    def is_base64(s):
        if not isinstance(s, str) or not s:
            return False
        try:
            s_clean = ''.join(s.strip().split())
            decoded = base64.b64decode(s_clean, validate=True)
            return base64.b64encode(decoded).decode() == s_clean
        except:
            return False

    encoded = spaghetti_encrypted
    decode = base64.b64decode(encoded.encode('utf-8'))
    decoded_str = decode.decode()
    salt_str = str(key.encode('utf-8'))[2:-1]
    if salt_str in decoded_str:
        decode1 = decoded_str.replace(salt_str, "", 1)
    else:
        print("Invalid key or invalid string. Exiting...")
        sys.exit()
    final = base64.b64decode(decode1.encode('utf-8')).decode('utf-8')
    return final

def inpt(message):
    class InputWindow(Gtk.Window):
        def __init__(self):
            super().__init__(title="LockBox")

            # Get screen height for max widget height
            display = Gdk.Display.get_default()
            monitor = display.get_monitor(0)
            geometry = monitor.get_geometry()
            screen_height = geometry.height
            self.max_widget_height = int(screen_height / 6)

            self.set_default_size(600, 300)

            # Outer vertical box for vertical centering
            self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.add(self.vbox)

            # Top spacer
            self.vbox.pack_start(Gtk.Box(), True, True, 0)

            # Label
            self.label = Gtk.Label(label=message)
            self.label.set_halign(Gtk.Align.CENTER)
            self.label.set_valign(Gtk.Align.CENTER)
            self.vbox.pack_start(self.label, False, False, 0)

            # Horizontal box for entry and button
            self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            self.hbox.set_halign(Gtk.Align.CENTER)
            self.vbox.pack_start(self.hbox, False, False, 0)

            # Entry
            self.entry = Gtk.Entry()
            self.entry.set_visibility(False)
            self.entry.set_hexpand(True)
            self.entry.set_vexpand(False)
            self.entry.connect("activate", self.on_submit)
            self.hbox.pack_start(self.entry, True, True, 0)

            # Button
            self.button = Gtk.Button(label="Submit")
            self.button.set_hexpand(False)
            self.button.set_vexpand(False)
            self.button.connect("clicked", self.on_submit)
            self.hbox.pack_start(self.button, False, False, 0)

            # Bottom spacer
            self.vbox.pack_start(Gtk.Box(), True, True, 0)

            # Connect to resize
            self.connect("configure-event", self.on_window_resize)

            self.user_input = None

        def on_window_resize(self, widget, event):
            # Height management
            h = min(event.height // 6, self.max_widget_height)
            self.hbox.set_size_request(-1, h)
            self.entry.set_size_request(-1, h)
            self.button.set_size_request(-1, h)

            # Width matching for label
            total_width = self.get_allocated_width()
            padding = 40
            label_width = min(total_width - padding, self.hbox.get_allocated_width())
            self.label.set_size_request(label_width, -1)

            # Dynamically scale label font with CSS (modern method)
            font_size = max(8, event.height // 15)
            css = Gtk.CssProvider()
            css.load_from_data(f"""
                label {{
                    font-size: {font_size}px;
                }}
            """.encode())
            self.label.get_style_context().add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_USER)

            return False


        def on_submit(self, widget):
            self.user_input = self.entry.get_text()
            Gtk.main_quit()

    win = InputWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    return win.user_input

# Example usage
masterpass = inpt("Master password:")

filepath = "psswd.txt"


class SecureListViewer(Gtk.Window):
    def __init__(self):
        super().__init__(title="LockBox")
        self.set_default_size(800, 600)

        self.new_entry_data = None  # Will hold (label, password) tuple from the add dialog

        # Main vertical box (for button + list)
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_vbox.set_margin_top(10)
        main_vbox.set_margin_bottom(10)
        main_vbox.set_margin_start(10)
        main_vbox.set_margin_end(10)
        self.add(main_vbox)

        # Top bar with + button
        top_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        main_vbox.pack_start(top_bar, False, False, 0)

        # Spacer to push button to the right
        top_bar.pack_start(Gtk.Box(), True, True, 0)

        # + Button
        add_button = Gtk.Button(label="+")
        add_button.set_tooltip_text("Add new entry")
        add_button.connect("clicked", self.on_add_clicked)
        top_bar.pack_start(add_button, False, False, 0)

        # Scrollable window for entries
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        main_vbox.pack_start(scrolled_window, True, True, 0)

        # Vertical container for rows
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        scrolled_window.add(self.vbox)

        # Load existing lines from file as before
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    line = decrypt(line, masterpass)
                    parts = line.split(r"\%%", 1)
                    label_text = parts[0]
                    hidden_text = parts[1] if len(parts) > 1 else ""

                    self.add_entry_row(label_text, hidden_text)
        except FileNotFoundError:
            print("File doesn't exist")
        except Exception as e:
            error_label = Gtk.Label(label=f"Error: {e}")
            self.vbox.pack_start(error_label, False, False, 0)

        self.show_all()

    def add_entry_row(self, label_text, hidden_text):
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        hbox.set_hexpand(True)
        hbox.set_vexpand(False)

        label = Gtk.Label(label=label_text)
        label.set_xalign(0)
        label.set_hexpand(False)
        label.set_vexpand(False)
        label.set_size_request(200, 50)
        hbox.pack_start(label, False, False, 0)

        entry = Gtk.Entry()
        entry.set_text(hidden_text)
        entry.set_visibility(False)
        entry.set_editable(False)
        entry.set_can_focus(False)
        entry.set_hexpand(True)
        entry.set_vexpand(False)
        entry.set_size_request(-1, 50)
        hbox.pack_start(entry, True, True, 0)

        button = Gtk.ToggleButton(label="Show")
        button.set_focus_on_click(False)
        button.set_hexpand(False)
        button.set_vexpand(False)
        button.set_size_request(-1, 50)
        button.connect("toggled", self.on_toggle_visibility, entry)
        hbox.pack_start(button, False, False, 0)

        hbox.set_size_request(-1, 50)
        self.vbox.pack_start(hbox, False, False, 0)

    def on_toggle_visibility(self, button, entry):
        visible = button.get_active()
        entry.set_visibility(visible)
        button.set_label("Hide" if visible else "Show")

    def on_add_clicked(self, button):
        dialog = Gtk.Dialog(title="Add New Entry", transient_for=self, flags=0)
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        dialog.set_default_size(300, 150)

        content_area = dialog.get_content_area()

        grid = Gtk.Grid(column_spacing=10, row_spacing=10, margin=10)
        content_area.add(grid)

        label_label = Gtk.Label(label="Label:")
        label_label.set_halign(Gtk.Align.START)
        grid.attach(label_label, 0, 0, 1, 1)

        label_entry = Gtk.Entry()
        grid.attach(label_entry, 1, 0, 1, 1)

        password_label = Gtk.Label(label="Password:")
        password_label.set_halign(Gtk.Align.START)
        grid.attach(password_label, 0, 1, 1, 1)

        password_entry = Gtk.Entry()
        password_entry.set_visibility(False)
        grid.attach(password_entry, 1, 1, 1, 1)

        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            label_text = label_entry.get_text().strip()
            password_text = password_entry.get_text().strip()
            if label_text and password_text:
                self.new_entry_data = (label_text, password_text)
                self.add_entry_row(label_text, password_text)
                AddEntry(label_text, password_text)
        dialog.destroy()



# Run the app
win = SecureListViewer()
win.connect("destroy", Gtk.main_quit)
Gtk.main()