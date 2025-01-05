from bdemo.part import Box, Cylinder

box1 = Box(9, 9, 3)
box2 = Box(3, 3, 6)
cyl1 = Cylinder(5, 3)
cyl2 = Cylinder(2, 3)
obj1 = cyl1 - cyl2
obj2 = box1 + box2
obj3 = box1 + cyl1
box1.add(cyl1)
print('box:', box1)

if __name__ == "__main__":
    import ocp_vscode as ov
    ov.show_object(obj1(), clear=True, tools=False, glass=False)
