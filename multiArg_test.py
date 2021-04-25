#!/usr/bin/python3

import argparse

def store_const_multiple(const, *destinations) :
    """Returns an `argparse.Action` class that sets multiple argument
    destinations (`destinations`) to `const`."""
    class store_const_multiple_action(argparse.Action) :
        def __init__(self, *args, **kwargs) :
            super(store_const_multiple_action, self).__init__(metavar = None, nargs = 0, const = const, *args, **kwargs)

        def __call__(self, parser, namespace, values, option_string = None) :
            for destination in destinations :
                setattr(namespace, destination, const)

    return store_const_multiple_action

def store_true_multiple(*destinations) :
    """Returns an `argparse.Action` class that sets multiple argument
    destinations (`destinations`) to `True`."""
    return store_const_multiple(True, *destinations)

ap = argparse.ArgumentParser()

ap.add_argument("--x", help = "Set `x`.", \
    action = "store_true", default = False)
ap.add_argument("--y", help = "Set `y`.", \
    action = "store_true", default = False)

ap.add_argument("--all", help = "Equivalent to `--x --y`.", \
    action = store_true_multiple("x", "y"))

args = ap.parse_args()

print("args.x", args.x)
print("args.y", args.y)
