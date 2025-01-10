from bdemo.primitives import Box, Cylinder


obj = Box(9, 9, 3, color="orange")
obj.add(Box(6, 6, 6, color="red"))
obj.add(Box(3, 3, 9, color="green"))
hole = obj.sub(Cylinder(1, 9, color="blue"))
obj.chamfer(hole.edges_added.values(), 0.2, color="pink")

for operation in obj.operations:
    print(operation)

if __name__ == "__main__":
    from ocp_vscode import show_object
    show_object(obj(), clear=True, tools=False, glass=False, black_edges=True)
