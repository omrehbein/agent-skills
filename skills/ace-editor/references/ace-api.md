# Ace API cheat sheet

Calls on `editor` (from `el.env.editor`, see the finder in `SKILL.md`) or on `editor.session`. Rows and columns are 0-based; only `gotoLine` takes a 1-based line. Reference: [Editor](https://ajaxorg.github.io/ace-api-docs/classes/src_editor.Editor.html), [EditSession](https://ajaxorg.github.io/ace-api-docs/classes/src_edit_session.EditSession.html).

## Read

| Call | Returns |
| --- | --- |
| `editor.getValue()` | whole document |
| `editor.session.getLength()` | number of rows |
| `editor.session.getLine(row)` / `getLines(first, last)` | one row / inclusive slice |
| `editor.session.getTextRange({ start, end })` | text inside a range |
| `editor.getSelectedText()`, `editor.getSelectionRange()` | current selection |
| `editor.getCursorPosition()` | `{ row, column }` |
| `editor.session.getMode().$id` | language mode, e.g. `ace/mode/yaml` |
| `editor.session.getTabString()`, `getTabSize()`, `getUseSoftTabs()` | indentation in use |
| `editor.getReadOnly()`, `editor.getOption(name)`, `editor.getOptions([names])` | state and options |
| `editor.getKeyboardHandler()?.$id` | `ace/keyboard/vim`, `ace/keyboard/emacs`… (`null` = default); key-driven input differs a lot there — stay with the API |

## Write

| Call | Effect |
| --- | --- |
| `editor.setValue(text, -1)` | replace everything, cursor at start |
| `editor.insert(text)` | insert at the cursor (replaces the selection) |
| `editor.session.insert({ row, column }, text)` | insert at a position |
| `editor.session.remove(range)`, `editor.session.replace(range, text)` | edit a range; plain `{ start, end }` objects work |
| `editor.find(needle, options)` then `editor.replace(text)` | replace the first match |
| `editor.findNext()`, `editor.findPrevious()` | move between matches of the last search |
| `editor.replaceAll(text, { needle, regExp, caseSensitive, wholeWord })` | replace every match, returns the count (`$1` works with `regExp`) |
| `editor.findAll(needle, options)` | selects every match (multi-cursor), returns the count; leave with `editor.exitMultiSelectMode()` and `editor.clearSelection()` |
| `editor.session.getUndoManager().startNewGroup()` | start a separate undo step before your change |
| `editor.undo()`, `editor.redo()`, `editor.session.getUndoManager().hasUndo()` | history |

## Cursor, selection, scrolling, folding

- `editor.gotoLine(line, column, false)` (1-based line), `editor.navigateTo(row, column)`, `editor.navigateFileEnd()`, `editor.selectAll()`, `editor.clearSelection()`, `editor.focus()`.
- `editor.scrollToLine(row, true, false)` then `editor.renderer.updateFull(true)` (renders immediately); `editor.getFirstVisibleRow()` / `editor.getLastVisibleRow()` then tell which rows a screenshot shows.
- Folded code is missing from the DOM and screenshots: `editor.session.unfold()` expands everything, `editor.session.foldAll()` folds, `editor.session.getAllFolds().length` counts folds.

## Commands

`editor.execCommand(name)` runs what a shortcut would; list them with `Object.keys(editor.commands.byName)`. Common: `selectall`, `undo`, `redo`, `find`, `replace`, `gotoline`, `togglecomment`, `foldall`, `unfoldall`.

## Options that change input

| Option | Effect |
| --- | --- |
| `behavioursEnabled`, `wrapBehavioursEnabled` | auto-pairing of quotes and brackets, wrapping selections |
| `enableAutoIndent` | indentation after Enter |
| `enableLiveAutocompletion`, `enableBasicAutocompletion`, `enableSnippets` | completion popups that capture Enter/Tab (only when the page loaded `ext-language_tools`) |
| `readOnly` | blocks user input; the API still writes |
| `useWorker` | background syntax validation → `session.getAnnotations()` |
| `tabSize`, `useSoftTabs`, `wrap` | layout of typed text |

Change several at once with `editor.setOptions({ ... })`.

## Events

- `editor.session.on('change', delta => ...)` — every document change.
- `editor.session.once('changeAnnotation', ...)` — validation results updated.
- `editor.session.on('changeMode', ...)` — language mode finished loading.
- `editor.on('changeSelection', ...)`, `editor.on('focus' | 'blur', ...)`.
- Remove listeners with `.off(name, handler)`.
