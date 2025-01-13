# Bumo

BUild123d Mutables Objects

An experimental package used to manage [Build123d](https://github.com/gumyr/build123d) objects by applying mutations on them.

It can be used:
- just out of curiosity, because it's a new way to build things;
- as a debug tool, using colors and debug mode;
- as a more object-oriented approach to build CAD parts.

![](./images/chamfers_and_fillets.png)

## Installation

This package [is registred on Pypi](https://pypi.org/project/bumo/), so you can either install it with Poetry:

    poetry add bumo

or with pip:

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

show_object(obj(), clear=True)
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

### Listing mutations

You can print the list of mutations and their properties:

```py
obj.info()
```

The previous example will produce the following table:

![](./images/info.png)

With:
- **Idx**: mutation index;
- **Id**: mutation id;
- **Type**: operation type;
- **Color**: faces color for this mutation;
- **f+**, **f~**, **f-**: amount of added/altered/removed faces on this mutation;
- **e+**, **e~**, **e-**: amount of added/altered/removed edges on this mutation;

### Moving objects

You can move objects with `move()`, all colors will be preserved. Note that you can still use the Build123d `*` operator before passing the object to the builder.

```py
obj = Builder(_.Box(12, 12, 2))
obj.add(_.Box(8, 8, 4))
obj.move(_.Location([-5, 2, 0]))
obj.sub(_.Rotation(25, 25, 0) * _.Cylinder(2.5, 10))
```

![](./images/move.png)

### Reusing mutations

Instead of returning a copy of the object, mutations return a `Mutation` object that can be used to retrieve the altered faces and edges. Mutations can also be accessed by querrying a builder index (ie. `obj[n]`). This is useful with fillets and chamfers:

```py
obj = Builder(_.Box(12, 12, 2))
obj.add(_.Box(8, 8, 4))
obj.fillet(obj[-1].edges_added(), 0.4)
hole = obj.sub(_.Cylinder(3, 4))
obj.chamfer(hole.edges_added()[0], 0.3)
```

![](./images/chamfers_and_fillets.png)

### Changing colors

On each mutation you can pass a specific color instead of the auto-generated-one:

```py
obj = Builder(_.Box(12, 12, 2), "orange")
obj.add(_.Box(8, 8, 4), "green")
obj.sub(_.Cylinder(3, 4), "violet")
```

![](./images/colors.png)

### Using the debug mode

You can turn one or several mutations in debug mode, so all the other faces will be translucent. Either by passing a debug attribute to mutations, or passing faces (even removed ones) to the debug method:

```py
obj = Builder(_.Box(12, 12, 2))
obj.add(_.Box(8, 8, 4))
obj.fillet(obj[-1].edges_added(), 0.4)
hole = obj.sub(_.Cylinder(3, 4))
obj.chamfer(hole.edges_added()[0], 0.3, debug=True)
obj.debug(obj[2].faces_altered()[0], "red")
# obj.debug(hole.faces_removed(), "red")
```

![](./images/debug.png)

### Alternative syntax

Alternatively you can use the operators `+=`, `-=`, `&=`, `*=` to add mutations. But beware that passing a color or debug mode will no longer be possible, neither storing the mutation to a variable (you can still get them with the `obj[n]` syntax):

```py
obj = Builder(_.Box(12, 12, 2))
obj += _.Box(8, 8, 4) # fuse
obj -= _.Cylinder(3, 4) # substract
obj &= _.Cylinder(5, 4) # intersect
obj *= _.Rotation(90) # move
```

Note that their counterpart `+`, `-`, `&`, `*` are not allowed.

### Configuring the builder

You can set builder attributes if necessary:

```py
Builder.default_color = "grey"
Builder.debug_alpha = 0.5
Builder.autocolor = False
Builder.color_palette = ColorPalette.INFERNO
```
