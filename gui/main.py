#!/usr/bin/python
from gi.repository import Gtk
import string_tables

UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='FileQuit' />
    </menu>
  </menubar>
  <toolbar name='ToolBar'>
    <toolitem action='FileQuit' />
  </toolbar>
</ui>
"""

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="BlueZ test case generator")

        self.set_default_size(450, 450)

        action_group = Gtk.ActionGroup("actions")
        action_filemenu = Gtk.Action("FileMenu", "File", None, None)
        action_group.add_action(action_filemenu)
        action_filequit = Gtk.Action("FileQuit", None, None, Gtk.STOCK_QUIT)
        action_filequit.connect("activate", lambda *a: Gtk.main_quit())
        action_group.add_action(action_filequit)

        uimanager = Gtk.UIManager()
        uimanager.add_ui_from_string(UI_INFO)
        uimanager.insert_action_group(action_group)
        self.add_accel_group(uimanager.get_accel_group())

        menubar = uimanager.get_widget("/MenuBar")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menubar, False, False, 0)

        toolbar = uimanager.get_widget("/ToolBar")
        box.pack_start(toolbar, False, False, 0)

        treestore = Gtk.TreeStore(str)
        r = treestore.append(None, ["HCI Command: Reset (0x03|0x0003) plen 0"])
        treestore.append(r, ["HCI Event: Command Complete (0x0e) plen 4"])
        r = treestore.append(None, ["HCI Command: Read Local Supported Features (0x04|0x0003) plen 0"])
        treestore.append(r, ["HCI Event: Command Complete (0x0e) plen 12"])
        r = treestore.append(None, ["HCI Command: Read Local Version Information (0x04|0x0001) plen 0"])
        treestore.append(r, ["HCI Event: Command Complete (0x0e) plen 12"])
        treeview = Gtk.TreeView(model=treestore)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Packets", renderer_text, text=0)
        treeview.append_column(column_text)
        box.pack_start(treeview, False, False, 0)

        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.add(Gtk.Label("Packet indicator:"))
        combo = Gtk.ComboBoxText()
        combo.set_entry_text_column(0)
        combo.connect("changed", self.on_combo_changed)
        for v in ["HCI Command (1)", "ACL Data (2)", "SCO Data (3)", "HCI Event (4)"]:
            combo.append_text(v)
        combo.set_active(0)
        grid.add(combo)
        box.pack_start(grid, False, False, 0)

        frame = Gtk.Frame(label="HCI Command")

        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.attach(Gtk.Label("OGF"), 0, 0, 1, 1)
        combo = Gtk.ComboBoxText()
        combo.set_entry_text_column(0)
        combo.connect("changed", self.on_combo_changed)
        for v in ["Link Control Commands (1)", "Link Policy Commands (2)",
                "Controller & Baseband Commands (3)",
                "Informational Parameters (4)", "Status Parameters (5)",
                "Testing Commands (6)", "LE Controller Commands (8)"]:
            combo.append_text(v)
        combo.set_active(0)
        grid.attach(combo, 1, 0, 1, 1)

        grid.attach(Gtk.Label("OCF"), 0, 1, 1, 1)
        combo = Gtk.ComboBoxText()
        combo.set_entry_text_column(0)
        combo.connect("changed", self.on_combo_changed)
        for i in string_tables.ogf_1:
            combo.append_text("%s (%d)" % (i[1], i[0]))
        combo.set_active(0)
        grid.attach(combo, 1, 1, 1, 1)

        frame.add(grid)
        box.pack_start(frame, False, False, 0)

        self.add(box)

    def on_combo_changed(self, combo):
        text = combo.get_active_text()
        if text is not None:
            print("Selected: %s" % text)

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
