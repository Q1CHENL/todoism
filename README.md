# todoism

A powerful yet easy-to-use todo TUI

## Screenshots

![UI](./assets/screenshot-latest.png)
![UI](./assets/screenshot-help-latest.png)

## Highlights

- Simple, intuitive interface
- Mouse support: click & scroll
- Easy task search
- Customizable: theme, sorting, and more
- Common Keyboard shortcuts support for editing
- Vim-like commands available for convenience

## Install and use

- Install: `pip install todoism`
- Run: `todoism` or `todo`
- Update: `pip install todoism --upgrade`
- Use: Invoke help message using command `:help` to see commonly used operations and commands

> [!NOTE]
> Some terminals does not support mouse click or strike through effect.
> **Ptyxis** (new default terminal for GNOME 47) does not fully support strikethrough effect. **Ghostty** does not has good support for bold text.
> You can turn them off in **preference panel** (open with `:pref` as specified in the help message)

### Keycode recording

When you first start todoism, you'll be prompted to record key combinations for text navigation.

- **CTRL + LEFT**: Move cursor one word left when editing text
- **CTRL + RIGHT**: Move cursor one word right when editing text
- **CTRL + SHIFT + LEFT**: Select text from cursor position to one word left
- **CTRL + SHIFT + RIGHT**: Select text from cursor position to one word right
- **ALT + LEFT**:
  - Move cursor to the beginning of the text
  - Jump to top task/category
- **ALT + RIGHT**:
  - Move cursor to the end of the text
  - Jump to bottom task/category

> [!NOTE]
> Some terminals like **Ghostty** may have built-in key bindings that conflict with the above. You need to disable them before recording.

## Develop

- Run with docker in dev mode with test files:
  - Build docker image: `docker build -t ubuntu-todoism .`
  - Run in project root: `./test/todocker.sh`

- Or run `python -m todoism --dev` directly (not recommended). Add `--profile` to enable profiling. (`--dev` and `--profile` are not available in PyPI installation)

- Normal Configuration and data files are located in `~/.todoism/`. Test ones are in `test/.todoism`

- Automated integration test (Experimental):
  - Install `wmctrl` with your package manager
  - Run `python test/integration.py` in project root
  - Read the instructions printed in the terminal carefully

> [!CAUTION]
> Todoism is currently under active development and backwards compatibility is not guaranteed as I refine features and data structures. Automatic data migration (tasks, categories, settings) between versions may not be fully supported. Please backup your data when needed. **v1.21 and lower versions are perticularly deprecated!**

## Contribute

Issues and PRs are welcome! Todoism is built from scratch with curses library. Please refer to the curses [docs](https://docs.python.org/3/library/curses.html#module-curses) and [how-to](https://docs.python.org/3/howto/curses.html) to get started.
