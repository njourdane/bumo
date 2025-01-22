# Bumo

**Bu**ild123d **m**utables **o**bjects

![](images/chamfers_and_fillets.png)

## Introduction

Bumo is a Python package that work with the [Build123d](https://github.com/gumyr/build123d) CAD library.

It essentially consists in a new class `Builder` used to update a CAD model: instead of creating a new instance of a CAD object each time an operation is made, the builder mutates to its new shape.

This slight difference on the behavior allows to:
- get more intuitive results when altering object attributes or when working with class inheritance;
- keep track of all the CAD object history, which can be used for various features, such as faces coloration based on operations.

The following instructions assumes you already know the basics of Build123d: if necessary please take a look at the [Build123d docs](https://build123d.readthedocs.io/en/latest/) before to continue.

## Installation

This package [is registred on Pypi](https://pypi.org/project/bumo/), so you can either install it with Poetry:

    poetry add bumo

or with pip:

    pip install bumo

## Getting started

### Simple example

Let's start with some basic operations:

```py
import build123d as _
from ocp_vscode import show_object
from bumo import Builder

b = Builder()

b += _.Box(8, 8, 2)
b -= _.Cylinder(2, 15)
b *= _.Rotation(0, 25, 0)
b &= _.Cylinder(4, 8)

show_object(b(), clear=True)
```

Wich will produce this:

![](images/basic.png)

For now there are no big differences here compared to the classical way to use Build123d, but let's analyze these 4 parts anyway:

1. **Imports**: respectively, the Build123d CAD library, the [ocp-vscode viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer/issues), and Bumo (I have a personal preference for named imports over wildcard imports, but do as you wish);
2. **Builder instantiation**;
3. **Applying mutations**: respectively, `fuse`, `substract`, `move`, and `intersect` (note that their counterparts `+`, `-`, `*`, `&` are not available);
4. **Show**: using ocp-vscode here, but any viewer should work (note that we must call the builder (`b()`) when passing it to the show function).

Parts 1. and 4. will always be the same here, so let's ignore them and focus on the builder-related stuff for the next examples.

### Listing mutations

You can print the list of mutations and their properties:

```py
b.info()
```

This will produce a table like this:

![](./images/info.png)

There is one row per muation, and their colors match the faces colors, which is convenient to quicly make a link between the operations and the altered faces.

Column details:
- **Idx**: mutation index;
- **Id**: mutation id;
- **Type**: operation type;
- **F+**, **F~**, **F-**: amount of added/altered/removed faces on this mutation;
- **E+**, **E~**, **E-**: amount of added/altered/removed edges on this mutation;

### Listing shapes

The info method is accessible from any mutation shapes attribute (`faces_altered`, `edges_removed`, etc.), for instance:

```py
b = Builder()
b += _.Box(1, 2, 3)
b.last.faces_added.info()
```

Will produce:

```
╒════════╤════════════════╤════════╤════════════════╤═══════════════╕
│ Hash   │ Type           │   Area │ Position       │ Orientation   │
╞════════╪════════════════╪════════╪════════════════╪═══════════════╡
│ 634e76 │ GeomType.PLANE │      6 │ [-0.5, -1, -2] │ [-0, 0, -0]   │
│ 75e78b │ GeomType.PLANE │      6 │ [-0.5, -1, -2] │ [-0, 0, -0]   │
│ fdc160 │ GeomType.PLANE │      3 │ [-0.5, -1, -2] │ [-0, 0, -0]   │
│ 7843d9 │ GeomType.PLANE │      3 │ [-0.5, -1, -2] │ [-0, 0, -0]   │
│ fc164c │ GeomType.PLANE │      2 │ [-0.5, -1, -2] │ [-0, 0, -0]   │
│ f6c299 │ GeomType.PLANE │      2 │ [-0.5, -1, -2] │ [-0, 0, -0]   │
╘════════╧════════════════╧════════╧════════════════╧═══════════════╛
```

### Extended syntax

The example above could also have been written like this:

```py
b = Builder()
b.add(_.Box(8, 8, 2))
b.sub(_.Cylinder(2, 15))
b.move(_.Rotation(0, 25, 0))
b.intersect(_.Cylinder(4, 8))
```

This syntax allows to store the mutation itself into an object for later use.

### Reusing mutations

`Mutation` objects can be used to retrieve the added, altered, removed and untouched faces or edges on this mutation (for instance when working with fillets and chamfers), and they can be accessed either with:
- the return value of a mutation (ex. `hole = b.sub()`);
- querrying a builder index (ex. `b[2]`);
- using the last attribute (ex. `b.last`);

```py
b = Builder()
b.add(_.Box(12, 12, 2))
b.add(_.Box(8, 8, 4))
b.fillet(b.last.edges_added(), 0.4)
hole = b.sub(_.Cylinder(3, 4))
b.chamfer(hole.edges_added()[0], 0.3)
```

![](./images/chamfers_and_fillets.png)

### Using the debug mode

You can turn one or several mutations in debug mode, so all the other faces will be translucent, either by:

- passing DEBUG to the `mode` argument of a mutation method (ex: `b.add(..., mode=DEBUG)`);
- passing DEBUG to mutation assignment operator (ex: `b += ..., DEBUG`);
- passing faces (even removed ones) to the debug method (ex: `b.debug(...)`).

```py
from bumo import Builder, DEBUG

b += _.Box(12, 12, 2)
b += _.Box(8, 8, 4)
# b += _.Box(8, 8, 4), DEBUG
b.fillet(b.last.edges_added, 0.4)
hole = b.sub(_.Cylinder(3, 4))
b.chamfer(hole.edges_added[0], 0.3, mode=DEBUG)
b.debug(b[2].faces_altered[0])
# b.debug(hole.faces_removed())
```

![](./images/debug.png)

### Changing colors

By default, mutations are colored using a color palette. Using the same `mode` used earlier, you can pass a specific color instead of the auto-generated-one:

```py
b = Builder()
b += _.Box(12, 12, 2), "orange"
b += _.Box(8, 8, 4), "green"
b += _.Cylinder(3, 4), "violet"
```

![](./images/colors.png)

### Mutation with builders

If necessary it is possible to pass an other builder to a mutation:

```py
b = Builder()
b.add(_.Box(12, 12, 2))

obj2 = Builder()
obj2.add(_.Box(8, 8, 4))

b.add(obj2)
b.sub(_.Cylinder(3, 4))
```

### Configuring the builder

You can configure Bumo according to your needs:

```py
from bumo import config

config.DEBUG_ALPHA = 0.5
config.COLOR_PALETTE = ColorPalette.INFERNO
```

Options are:

- **COLOR_PALETTE**: The color palette to use when auto_color is enabled (`ColorPalette.VIRIDIS`);
- **DEBUG_ALPHA**: The alpha value used for translucent shapes in debug mode (`0.2`);
- **DEFAULT_COLOR**: The default color to be used when a color is passed to a mutation (`Color("orange")`);
- **DEFAULT_DEBUG_COLOR**: The default color to be used when using the debug mode (default: `Color("red")`);
- **INFO_COLOR**: Set to False to disable terminal colors in the info table (default: `True`);
- **INFO_TABLE_FORMAT** = The [table format](https://github.com/astanin/python-tabulate?tab=readme-ov-file#table-format) used in the info table (default: `"fancy_outline"`);
- **COLUMNS_MUTATIONS**: The columns to display in mutations info tables, among: idx, label, type, color_hex, color_name, f+, f~, f-, e+, e~, e- (default: `["idx", "label", "type", "f+", "f~", "f-", "e+", "e~", "e-"]`);
- **COLUMNS_SHAPES**: The columns to display in shapes info tables, among: hash, type, area, color_hex, color_name. (default: `["hash", "type", "area", "position", "orientation"]`).
