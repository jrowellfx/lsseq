.ll 76
.na
.hy 0
.pl 1
expandseq/condenseseq - two command line utilities that expose the basic functionality
of the python-module "seqLister.py"
functions "expandSeq()" and "condenseSeq()".  These functions
translate back and forth between a condensed form for listing sequences of numbers
and plain lists of numbers.  Lists of numbers in this condensed format
are commonly used by various computer programs dealing with sequences of
images such as render farm management tools (like smedge), image sequence viewers (like rv)
or "ls" commands (like lsseq) to list frames from CG-animation
or video footage which has been saved as a sequence of individually numbered frames.

The "expandseq" and "condenseseq" commands enhance the simple behavior of the "expandSeq()"
and "condenseSeq()" python functions by adding the ability to print out
the lists in various forms.  eg.; comma, space or newline separators
as well as sorting the
lists,
reversing order, and mixing and matching expanded and condensed formats as arguments on the command
line.
