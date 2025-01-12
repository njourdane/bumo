import build123d as _
from bumo import Builder

obj = Builder(_.Box(12, 12, 2), "orange")
obj.add(_.Box(8, 8, 4), "green")
obj.fillet(obj[-1].edges_added(), 0.4, color="yellow")
hole = obj.sub(_.Cylinder(3, 4), "violet")
obj.chamfer(hole.edges_added()[0], 0.3, color="blue")

obj.info()

if __name__ == "__main__":
    from ocp_vscode import show_object
    show_object(obj(), clear=True, tools=False, glass=False, black_edges=True)
