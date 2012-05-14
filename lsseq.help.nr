.ll 70
.na
.hy 0
.pl 1
List directory contents (akin to /bin/ls) while condensing image
sequences to one entry each. Filenames that are part of image
sequences are assumed to be of the form:

.in +4 
<descriptiveName>.<frameNum>.<imgExtension>
.in -4 

where <imgExtension>
is drawn from a default list of image extensions (see option -i)
or they can be set with the environment variable
OIC_IMAGE_EXTENSION=exr:jpg:tif (for example).
Similarly there is an OIC_MOV_EXTENSION environment variable
for movie file extensions.

%(prog)s will first list all non-image-sequence files followed by
the list of image sequences as such:

.in +4
.nf
$ %(prog)s
[output of /bin/ls minus image sequences]
[list of images sequences]
.fi
.in -4
