#
# Untitled Word Game makefile
# assembles source code, optionally builds a disk image and mounts it
#
# original by Quinn Dunki on 2014-08-15
# One Girl, One Laptop Productions
# http://www.quinndunki.com/blondihacks
#
# adapted by 4am on 2022-03-19
#

# third-party tools required to build

# https://sourceforge.net/projects/acme-crossass/
ACME=acme

BUILDDISK=build/untitled.dsk

asm:
	mkdir -p build
	touch build/log
	$(ACME) -r build/untitled.lst src/untitled.a 2>build/log
	$(ACME) -r build/0boot.lst src/0boot.a 2>>build/log

dist: asm
	split -d -b256 build/0boot build/0boot
	cat build/0boot00 > "$(BUILDDISK)"
	dd if=/dev/null of="$(BUILDDISK)" bs=1 count=1 seek=3584 2>>build/log
	cat build/0boot01 >> "$(BUILDDISK)"
	dd if=/dev/null of="$(BUILDDISK)" bs=1 count=1 seek=4K 2>>build/log
	cat build/UNTITLED >> "$(BUILDDISK)"
	dd if=/dev/null of=$(BUILDDISK) bs=1 count=1 seek=140K 2>>build/log

clean:
	rm -rf build/

mount:
	open "$(BUILDDISK)"

all: clean dist mount

al: all
