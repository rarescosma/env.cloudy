PREFIX?=$(HOME)
BINDIR?=$(PREFIX)/bin

all: dist/cloudy

dist/cloudy:
	pyinstaller --onefile cloudy/cloudy.py

install: dist/cloudy
	mkdir -p $(DESTDIR)$(BINDIR)
	cp dist/cloudy $(DESTDIR)$(BINDIR)/
	chmod 755 ${DESTDIR}${BINDIR}/cloudy

clean:
	rm -rf dist build *.spec
	rm -f ${DESTDIR}${BINDIR}/cloudy
