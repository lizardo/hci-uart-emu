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

        self.current_frame = None
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

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        menubar = uimanager.get_widget("/MenuBar")
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
        combo = Gtk.ComboBox.new_with_entry()
        self.set_model(combo, string_tables.pkt_indicator)
        combo.connect("changed", self.packet_selected, box)
        grid.add(combo)
        box.pack_start(grid, False, False, 0)

        self.add(box)

    def set_model(self, combo, data):
        liststore = Gtk.ListStore(int, str)
        for (i, text) in data:
            liststore.append((i, "%s (%d)" % (text, i)))

        combo.set_model(liststore)
        if len(data) > 10:
            combo.set_wrap_width(3)
        combo.set_entry_text_column(1)

    def create_packet_frame(self, pkt):
        if pkt == 1:
            frame = Gtk.Frame(label="HCI Command")

            grid = Gtk.Grid()
            grid.set_column_spacing(10)

            grid.attach(Gtk.Label("OGF"), 0, 0, 1, 1)
            #combo.set_active(0)
            combo_ocf = Gtk.ComboBox.new_with_entry()
            combo = Gtk.ComboBox.new_with_entry()
            self.set_model(combo, string_tables.ogf_list)
            combo.connect("changed", self.ogf_selected, combo_ocf)
            grid.attach(combo, 1, 0, 1, 1)

            grid.attach(Gtk.Label("OCF"), 0, 1, 1, 1)
            grid.attach(combo_ocf, 1, 1, 1, 1)

            frame.add(grid)
        else:
            frame = Gtk.Frame(label="Unsupported packet")
            frame.add(Gtk.Label("Packet not supported!"))

        return frame

    def packet_selected(self, combo, box):
        it = combo.get_active_iter()
        if it is None:
            return
        pkt = combo.get_model()[it][0]
        frame = self.create_packet_frame(pkt)
        if self.current_frame is not None:
            self.current_frame.destroy()
        box.pack_start(frame, False, False, 0)
        frame.show_all()
        self.current_frame = frame

    def ogf_selected(self, combo, combo_ocf):
        it = combo.get_active_iter()
        if it is None:
            return
        ogf = combo.get_model()[it][0]
        self.set_model(combo_ocf, string_tables.ocf[ogf])
        combo_ocf.get_child().set_text("")
        combo_ocf.set_active_iter(None)

win = MainWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
