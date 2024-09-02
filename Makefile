PROJECT=cloudy
ENTRYPOINT=$(PROJECT)/$(PROJECT).py
PREFIX?=$(HOME)
BINDIR?=$(PREFIX)/bin
BUILDPATH=dist/static
BUILD_VERSION:=latest
ARCH=linux-x86_64

all: dist/$(PROJECT)

dist/$(PROJECT): .venv/freeze
	. .venv/bin/activate && pyinstaller --onefile $(ENTRYPOINT)

install: dist/$(PROJECT)
	mkdir -p $(DESTDIR)$(BINDIR)
	install -m 755 dist/$(PROJECT) $(DESTDIR)$(BINDIR)/

clean:
	rm -rf dist build *.spec __pycache__ *.egg-info .python-version .venv

.python-version:
	pyenv local 3.12

.venv/freeze: .python-version
	test -f .venv/bin/activate || python3 -mvenv .venv --prompt $(PROJECT)
	. .venv/bin/activate && pip install -e . && pip freeze > .venv/freeze

build_static:
	./portable/alpine-build.sh

pack_static:
	@rm -rf pack
	@mkdir -p pack
	@cd ${BUILDPATH} && tar -czvf ${PROJECT}-${BUILD_VERSION}-$(ARCH).tar.gz *
	@mv ${BUILDPATH}/${PROJECT}-${BUILD_VERSION}-$(ARCH).tar.gz pack
	@openssl sha256 < pack/${PROJECT}-${BUILD_VERSION}-$(ARCH).tar.gz | sed 's/^.* //' > pack/${PROJECT}-${BUILD_VERSION}-$(ARCH).sha256sum
	@cat pack/${PROJECT}-${BUILD_VERSION}-$(ARCH).sha256sum
