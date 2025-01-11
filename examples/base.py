import build123d as _
from bdemo.part import Part

Part.default_color = "red"

obj = Part(_.Box(9, 9, 3), color="orange")
# obj.move(_.Location([3, 0, 0]) * _.Rotation(15, 0, 0))
obj.add(_.Box(6, 6, 6))
obj.add(_.Box(3, 3, 9), color="green")
obj.sub(_.Cylinder(1, 9), color="blue")

# for face_hash, face in obj[-1].faces.items():
#     print(obj.get_face_operation(face), face_hash)

for operation in obj.operations:
    print(operation)

if __name__ == "__main__":
    import ocp_vscode as ov
    ov.show_object(obj(), clear=True, tools=False, glass=False, black_edges=True)
