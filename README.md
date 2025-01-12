# Bumo

BUild123d Mutables Objects

An experimental package used to manage [Build123d](https://github.com/gumyr/build123d) objects by applying mutations on them.

It can be used:
- just out of curiosity, because it's a new way to build things;
- as a debug tool, using colors and debug mode;
- as a higher-level interface for Build123d;
- as a more object-oriented approach to build CAD parts.

![](./images/chamfers_and_fillets.png)

## Installation

    poetry install bumo

or using pip:

    pip install bumo

## Getting started

Bumo is not a cad library on its own and does not aim to replace Build123d, you should take a look at [the Build123d docs](https://build123d.readthedocs.io/en/latest/) before using it.

*Note: In the following examples we will use [ocp vscode](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues), but any other viewer should work.*

### Instantiating the builder

First things first, let's instanciate a Bumo builder and pass a Build123d part into it. Note that we must call the object (`obj()`) when passing it to the show function.

```py
import build123d as _
from ocp_vscode import show_object
from bumo import Builder

obj = Builder(_.Box(12, 12, 2))

show_object(obj())
```

![](./images/box.png)

### Adding mutations

When applying an operation, instead of returning a copy of the modified object, the builder mutates the object:

```py
obj = Builder(_.Box(12, 12, 2))
obj.add(_.Box(8, 8, 4))
obj.sub(_.Cylinder(3, 4))
```

![](./images/base.png)

Note that you can also pass an other builder to a mutation:

```py
obj = Builder(_.Box(12, 12, 2))
obj2 = Builder(_.Box(8, 8, 4))
obj.add(obj2)
obj.sub(_.Cylinder(3, 4))
```

### Adding colors

On each mutation you can pass a `color`, because coloring object faces is useful and funny:

```py
obj = Builder(_.Box(12, 12, 2), "orange")
obj.add(_.Box(8, 8, 4), "green")
obj.sub(_.Cylinder(3, 4), "violet")
```

![](./images/colors.png)

### Moving objects

You can move objects with `move()`, all colors will be preserved. Note that you can still use the Build123d `*` operator before passing the object to the builder.

```py
obj = Builder(_.Box(12, 12, 2), "orange")
obj.add(_.Box(8, 8, 4), "green")
obj.move(_.Location([-5, 2, 0]))
obj.sub(_.Rotation(25, 25, 0) * _.Cylinder(2.5, 10), "violet")
```

![](./images/move.png)

### Reusing mutations

Instead of returning a copy of the object, mutations return a `Mutation` object that can be used to retrieve the altered faces and edges. Mutations can also be accessed by querrying a builder index (ie. `obj[n]`). This is useful with fillets and chamfers:

```py
obj = Builder(_.Box(12, 12, 2), "orange")
obj.add(_.Box(8, 8, 4), "green")
obj.fillet(obj[-1].edges_added(), 0.4, color="yellow")
hole = obj.sub(_.Cylinder(3, 4), "violet")
obj.chamfer(hole.edges_added()[0], 0.3, color="blue")
```

![](./images/chamfers_and_fillets.png)

You may notice that the "top box" is not green anymore: this is because the yellow part produced by the fillet shares no edge with the top box, so the part is considered to be new and not just altered. In the other hand, the hole kept its pink color, because the bottom circular edge is still connected to the box.

### Using the debug mode

You can turn one or several mutations in debug mode, so all the other faces will be translucent. Either by passing a debug attribute to mutations, or passing faces to the debug method:

```py
obj = Builder(_.Box(12, 12, 2), "orange")
obj.add(_.Box(8, 8, 4), "green")
obj.fillet(obj[-1].edges_added(), 0.4, color="yellow")
obj.debug(obj[-1].faces_altered()[0], "red")
hole = obj.sub(_.Cylinder(3, 4), "violet")
obj.chamfer(hole.edges_added()[0], 0.3, color="blue", debug=True)
```

![](./images/debug.png)

### Configuring the builder

You can set builder attributes if necessary:

```py
Builder.default_color = "grey"
Builder.debug_alpha = 0.5
```
