import argparse

def store_const_multiple(const, *destinations) :
    class store_const_multiple_action(argparse.Action) :
        def __init__(self, *args, **kwargs) :
            super(store_const_multiple_action, self).__init__( \
                metavar = None, nargs = 0, const = const, *args, **kwargs)

        def __call__(self, parser, namespace, values, option_string = None) :
            for d in destinations :
                setattr(namespace, d, const)

    return store_const_multiple_action

def store_true_multiple(*destinations) :
    return store_const_multiple(True, *destinations)

ap = argparse.ArgumentParser()

ap.add_argument("--x", dest="x", help = "Set x to True.",
    action = "store_true", default = False)
ap.add_argument("--X", dest="x", help = "Set x to False.",
    action = "store_false")

ap.add_argument("--y", dest="y", help = "Set y to True.",
    action = "store_true", default = False)
ap.add_argument("--Y", dest="y", help = "Set y to False.",
    action = "store_false")

ap.add_argument("--all", help = "Equivalent to `--x --y`.",
    action = store_true_multiple("x", "y"))

args = ap.parse_args()

print("args.x", args.x)
print("args.y", args.y)
