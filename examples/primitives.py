from bdemo.primitives import Box, Cylinder

obj = Box(9, 9, 3, color="orange")
obj.add(Box(6, 6, 6), color="red")
obj.add(Box(3, 3, 9), color="green")
obj.sub(Cylinder(1, 9), color="blue")

for operation in obj.operations:
    print(operation)

if __name__ == "__main__":
    import ocp_vscode as ov
    ov.show_object(obj(), clear=True, tools=False, glass=False)
