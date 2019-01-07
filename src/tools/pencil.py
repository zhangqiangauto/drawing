# pencil.py

from gi.repository import Gtk, Gdk, Gio, GLib
import cairo

from .tools import ToolTemplate

class ToolPencil(ToolTemplate):
	__gtype_name__ = 'ToolPencil'

	use_size = True

	def __init__(self, window, **kwargs):
		super().__init__('pencil', _("Pencil"), 'document-edit-symbolic', window)
		self.past_x = -1.0
		self.past_y = -1.0
		self._path = None
		self.main_color = None

		self.selected_shape_label = _("Round")
		self.selected_cap_id = cairo.LineCap.ROUND
		self.selected_join_id = cairo.LineCap.ROUND
		self.use_dashes = False

		self.add_tool_action_enum('pencil_shape', 'round', self.on_change_active_shape)
		self.add_tool_action_boolean('pencil_dashes', self.use_dashes, self.set_dashes_state)

	def set_dashes_state(self, *args):
		if not args[0].get_state():
			self.use_dashes = True
			args[0].set_state(GLib.Variant.new_boolean(True))
		else:
			self.use_dashes = False
			args[0].set_state(GLib.Variant.new_boolean(False))

	def on_change_active_shape(self, *args):
		state_as_string = args[1].get_string()
		if state_as_string == args[0].get_state().get_string():
			return
		args[0].set_state(GLib.Variant.new_string(state_as_string))
		if state_as_string == 'thin':
			self.selected_cap_id = cairo.LineCap.BUTT
			self.selected_join_id = cairo.LineJoin.BEVEL
			self.selected_shape_label = _("Thin")
		elif state_as_string == 'square':
			self.selected_cap_id = cairo.LineCap.SQUARE
			self.selected_join_id = cairo.LineJoin.MITER
			self.selected_shape_label = _("Square")
		else:
			self.selected_cap_id = cairo.LineCap.ROUND
			self.selected_join_id = cairo.LineJoin.ROUND
			self.selected_shape_label = _("Round")

	def get_options_model(self):
		builder = Gtk.Builder.new_from_resource("/com/github/maoschanz/Drawing/tools/ui/pencil.ui")
		return builder.get_object('options-menu')

	def get_options_label(self):
		return self.selected_shape_label

	def on_motion_on_area(self, area, event, surface, event_x, event_y):
		self.restore_pixbuf()
		w_context = cairo.Context(self.window.get_surface())
		w_context.set_line_cap(self.selected_cap_id)
		w_context.set_line_join(self.selected_join_id)
		w_context.set_line_width(self.tool_width)
		w_context.set_source_rgba(self.main_color.red, self.main_color.green, \
				self.main_color.blue, self.main_color.alpha)
		if self.use_dashes:
			w_context.set_dash([2*self.tool_width, 2*self.tool_width])
		if self.past_x == -1.0:
			(self.past_x, self.past_y) = (self.x_press, self.y_press)
			w_context.move_to(self.x_press, self.y_press)
			self._path = w_context.copy_path()
		else:
			w_context.append_path(self._path)
		w_context.line_to(event_x, event_y)
		w_context.stroke_preserve() # draw the line without closing the path
		self._path = w_context.copy_path()
		self.non_destructive_show_modif()
		self.past_x = event_x
		self.past_y = event_y

	def on_press_on_area(self, area, event, surface, tool_width, left_color, right_color, event_x, event_y):
		self.x_press = event_x
		self.y_press = event_y
		self.tool_width = tool_width
		if event.button == 3:
			self.main_color = right_color
		else:
			self.main_color = left_color

	def on_release_on_area(self, area, event, surface, event_x, event_y):
		self.past_x = -1.0
		self.past_y = -1.0
		self.apply_to_pixbuf()

