import build123d as _
from bumo import Builder

Builder.default_color = "grey"

obj = Builder(_.Box(9, 9, 3), color="orange")
# obj.move(_.Location([3, 0, 0]) * _.Rotation(15, 0, 0))
obj.add(_.Box(6, 6, 6))
obj.add(_.Box(3, 3, 9), color="green")
hole = obj.sub(_.Cylinder(1, 9), color="blue")
obj.chamfer(hole.edges_added()[0], 0.2, color="pink")

for mutation in obj.mutations:
    print(mutation)

if __name__ == "__main__":
    from ocp_vscode import show_object
    show_object(obj(), clear=True, tools=False, glass=False, black_edges=True)
