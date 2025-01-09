from bdemo.part_primitives import Box, Cylinder

obj = Box(9, 9, 3)
obj.add(Box(3, 3, 6))
obj.sub(Cylinder(1, 6))

for operation in obj.operations:
    print(operation, list(operation.faces.keys()))

if __name__ == "__main__":
    import ocp_vscode as ov
    ov.show_object(obj(), clear=True, tools=False, glass=False)
