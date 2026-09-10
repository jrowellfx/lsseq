# Makefile for installing/uninstalling the lsseq(1) man page.
#
# lsseq itself is installed via pip (see README.md); pip has no
# mechanism for installing man pages, so this Makefile handles that
# one job on the side. It installs nothing else and does not build
# anything -- 'make install' just copies lsseq.1 into place, and
# 'make uninstall' removes it again.
#
# Typical usage (system-wide, matching the /usr/local/venv setup
# described in the README):
#
#     $ sudo make install
#     $ man lsseq
#     ...
#     $ sudo make uninstall
#
# Installing to a user-writable prefix instead (no sudo required),
# provided that prefix's man dir is on your MANPATH:
#
#     $ make install PREFIX=$HOME/.local
#
# Packaging into a staging root (e.g. for building a distro package)
# via DESTDIR, keeping PREFIX as the path the package will eventually
# be installed to:
#
#     $ make install DESTDIR=/tmp/pkgroot PREFIX=/usr/local

# Where the man page lives in this repo.
MANSRCDIR ?= man
MANPAGE   := lsseq.1
SECTION   := 1

# Where it gets installed. PREFIX/MANPREFIX can be overridden on the
# command line, e.g. `make install PREFIX=/usr`. DESTDIR is prepended
# for staged/packaged installs and is empty by default.
#
PREFIX     ?= /usr/local
MANPREFIX  ?= $(PREFIX)/share/man
MANDIR     := $(MANPREFIX)/man$(SECTION)

DESTDIR    ?=

INSTALL         ?= install
INSTALL_DATA    ?= $(INSTALL) -m 644
GZIP            ?= gzip

.PHONY: all install install-compressed uninstall help

all: help

help:
	@echo "lsseq man-page installer (lsseq itself is installed via pip)"
	@echo ""
	@echo "  make install             install $(MANPAGE) (uncompressed)"
	@echo "  make install-compressed  install $(MANPAGE).gz instead"
	@echo "  make uninstall           remove whichever of the above was installed"
	@echo ""
	@echo "Current install location: $(DESTDIR)$(MANDIR)/$(MANPAGE)[.gz]"
	@echo "Override with, e.g.: make install PREFIX=/usr"

install: $(MANSRCDIR)/$(MANPAGE)
	mkdir -p $(DESTDIR)$(MANDIR)
	$(INSTALL_DATA) $(MANSRCDIR)/$(MANPAGE) $(DESTDIR)$(MANDIR)/$(MANPAGE)
	@-mandb -q $(DESTDIR)$(MANPREFIX) >/dev/null 2>&1 || true
	@echo "Installed $(DESTDIR)$(MANDIR)/$(MANPAGE)"

install-compressed: $(MANSRCDIR)/$(MANPAGE)
	mkdir -p $(DESTDIR)$(MANDIR)
	$(GZIP) -9 -c $(MANSRCDIR)/$(MANPAGE) > $(DESTDIR)$(MANDIR)/$(MANPAGE).gz
	chmod 644 $(DESTDIR)$(MANDIR)/$(MANPAGE).gz
	@-mandb -q $(DESTDIR)$(MANPREFIX) >/dev/null 2>&1 || true
	@echo "Installed $(DESTDIR)$(MANDIR)/$(MANPAGE).gz"

uninstall:
	rm -f $(DESTDIR)$(MANDIR)/$(MANPAGE) $(DESTDIR)$(MANDIR)/$(MANPAGE).gz
	@-mandb -q $(DESTDIR)$(MANPREFIX) >/dev/null 2>&1 || true
	@echo "Removed $(DESTDIR)$(MANDIR)/$(MANPAGE)[.gz]"
