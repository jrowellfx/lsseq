import subprocess
import shutil
import sys
import os

extraFiles = [ \
    "../testdir/adir", \
    "../testdir/bdir", \
    "../testdir/cdir", \
    "../testdir/ddir", \
    "../testdir/edir", \
    "../testdir/fdir", \
    "../testdir/gdir", \
    "../testdir/hdir", \
    "../testdir/idir", \
    "../testdir/jdir", \
    "../testdir/kdir", \
    "../testdir/ldir", \
    "../testdir/mdir", \
    "../testdir/ndir", \
    "../testdir/pdir", \
    "../testdir/qdir", \
    ]

extraLsArgList = [ \
    [], \
    ["fff"],  \
    extraFiles,  \
    ["-C"] + extraFiles,  \
    ["-C", "fff"] + extraFiles, \
    ["-x"] + extraFiles,  \
    ["-x", "fff"] + extraFiles, \
]

i = 1

def testRun(extraLsArg) :
    global extraFiles
    global i

    print("--- Test", i, ["ls", "-d"] + extraLsArg, "---")
    result = subprocess.run(["ls", "-d"] + extraLsArg , capture_output=True, text=True)
    print("---")

    print("len(stdout): ", len(result.stdout))
    print("stdout:")
    ## print(result.stdout, end= ('' if len(result.stdout) > 0 else '\n'))
    print(result.stdout, end= '')
    print("---")

    print("len(stderr): ", len(result.stderr))
    print("stderr:", sep='', end='')
    ## print(result.stderr, end= ('' if len(result.stderr) > 0 else '\n'))
    print(result.stderr, end='')

    print("---")
    print("error code: ", result.returncode)
    print("")

    i += 1


# if sys.stdout.isatty():
    ## You're running in a real terminal
# else:
    ## You're being piped or redirected

cols, rows = shutil.get_terminal_size()
## print("From shutil.get_terminal_size()")
## print("cols:", cols)
## print("rows:", rows)

## print(os.environ["PATH"])
## print(os.environ["COLUMNS"]) # Note: COLUMNS is NOT an env-var. i.e. not 'exported'

envCols = "aaa"
try :
    envCols = os.environ["COLUMNS"]
except:
    envCols = "30"

print("envCols:", envCols)

# But this will set it, so will have proper effect on run(["ls -C"])
os.environ["COLUMNS"] = str(cols)

for extraArg in extraLsArgList :
    testRun(extraArg)

