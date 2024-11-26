import starlark as sl

glb = sl.Globals.standard()
mod = sl.Module()


def g(x):
    print(f"g called with {x}")
    return 2 * x


mod.add_callable("g", g)

ast = sl.parse("a.star", "g(x=1)")


def load(name):
    raise FileNotFoundError(name)


sl.eval(mod, ast, glb, sl.FileLoader(load))
