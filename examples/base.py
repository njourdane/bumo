import build123d as _
from ocp_vscode import show_object
from bumo import Builder


b = Builder()
b.add(_.Box(12, 12, 2))
b.add(_.Box(8, 8, 4))
b.fillet(b[-1].edges_added(), 0.4)
hole = b.sub(_.Cylinder(3, 4))
b.chamfer(hole.edges_added().first, 0.3)

b.info()
show_object(b(), clear=True, tools=False, glass=False, black_edges=True)
