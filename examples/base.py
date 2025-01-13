import build123d as _
from ocp_vscode import show_object
from bumo import Builder


obj = Builder(_.Box(12, 12, 2))
obj.add(_.Box(8, 8, 4))
obj.fillet(obj[-1].edges_added(), 0.4)
hole = obj.sub(_.Cylinder(3, 4))
obj.chamfer(hole.edges_added()[0], 0.3)

obj.info()
show_object(obj(), clear=True, tools=False, glass=False, black_edges=True)
