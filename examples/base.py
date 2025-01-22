import build123d as _
from ocp_vscode import show_object
from bumo import Builder, config # , DEBUG

config.DEFAULT_COLOR = _.Color("orange")

b = Builder()
b += _.Box(12, 12, 2)
b += _.Box(8, 8, 4)
b.fillet(b.last.edges_added, 0.4) # , DEBUG
hole = b.sub(_.Cylinder(3, 4))
b.chamfer(hole.edges_added.first, 0.3)
# b.debug(b.last.faces_added)

b.info()
hole.faces_added.info()
show_object(b(), clear=True, tools=False, glass=False, black_edges=True)
