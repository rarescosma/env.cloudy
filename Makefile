PROJECT=cloudy
ENTRYPOINT=$(PROJECT)/$(PROJECT).py
PREFIX?=$(HOME)
BINDIR?=$(PREFIX)/bin

all: dist/$(PROJECT)

dist/$(PROJECT): .venv/freeze
	. .venv/bin/activate && pyinstaller --onefile $(ENTRYPOINT)

install: dist/$(PROJECT)
	mkdir -p $(DESTDIR)$(BINDIR)
	install -m 755 dist/$(PROJECT) $(DESTDIR)$(BINDIR)/

clean:
	rm -rf dist build *.spec __pycache__ *.egg-info .python-version .venv

.python-version:
	pyenv local 3.11.1

.venv/freeze: .python-version
	test -f .venv/bin/activate || python3 -mvenv .venv --prompt $(PROJECT)
	. .venv/bin/activate && pip install -e . && pip freeze > .venv/freeze
