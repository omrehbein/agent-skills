---
name: ace-editor
description: "Use when browser automation must read, replace or fix text inside an Ace code editor (`.ace_editor`) — e.g. AWS console JSON policy editors (IAM, KMS key policy, S3 bucket policy, SCP), Cloudscape/awsui code editors, Cloud9-style editors, react-ace. Also use when text typed into a web code editor comes out mangled (missing/duplicated quotes or brackets, doubled indentation, stray characters) or when the screenshot/DOM shows only part of the document."
---

# Ace editor automation

Ace is not a normal `<input>`. It renders only the visible lines (virtualized DOM) and receives keys through a hidden `textarea.ace_text-input`, with auto-pairing of quotes/brackets and auto-indent on Enter. So:

- **Never read content from the DOM, `read_page` or screenshots** — `.ace_text-layer` holds only visible rows.
- **Never type code key by key** (`type` action, `fill`) — newlines get auto-indented on top of your own spaces and dropped keys corrupt JSON. Use the editor API via JavaScript.

## 1. Get the editor instance

Run in the page with whatever JavaScript-evaluation capability your agent has (Playwright `page.evaluate`, Puppeteer, Chrome DevTools Protocol `Runtime.evaluate`, a browser MCP server's evaluate/javascript tool, or a built-in browser tool):

```js
const els = [...document.querySelectorAll('.ace_editor')].filter(e => e.offsetParent); // visible only
// narrow when there are several: document.querySelector('#policy-editor-container .ace_editor')
const editor = els[0]?.env?.editor; // set by ace.edit(); works even when window.ace is not global
({ count: els.length, found: !!editor, lines: editor?.session.getLength() })
```

Do **not** call `ace.edit(el)` on an element without `el.env` — it creates a second editor over the page's one.

## 2. Read / replace / patch

```js
const editor = document.querySelector('.ace_editor').env.editor;
editor.getValue();                          // full document
editor.setValue(newText, -1);               // replace all; -1 = cursor at start; fires 'change' so the app (React/Cloudscape onChange) sees it; undoable
// targeted fix without rewriting everything:
editor.find('aaAllow', { wrap: true, caseSensitive: true, wholeWord: false }) && editor.replace('Allow');
editor.replaceAll('"Allow"', { needle: '"Deny"' }); // replaceAll(replacement, options)
editor.gotoLine(11, 0, false);              // 1-based row, 0-based column
editor.session.getAnnotations();            // Ace worker diagnostics [{row, column, text, type}]
```

For JSON, build the value with `JSON.stringify(obj, null, 2)` (or 4 to match the page) instead of hand-writing strings.

## 3. Fallback: no `env` (bundled app, custom construction)

Paste into the hidden textarea — Ace inserts pasted text verbatim (no auto-pairing, no auto-indent):

```js
const root = document.querySelector('.ace_editor');
const ta = root.querySelector('textarea.ace_text-input');
ta.focus();
ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'a', code: 'KeyA', keyCode: 65, which: 65, ctrlKey: true, bubbles: true, cancelable: true })); // select all (use metaKey on macOS)
const dt = new DataTransfer(); dt.setData('text/plain', newText);
ta.dispatchEvent(new ClipboardEvent('paste', { clipboardData: dt, bubbles: true, cancelable: true }));
```

Alternative with the textarea focused and everything selected: `document.execCommand('insertText', false, newText)`.

Without JavaScript at all (pure computer-use): put the text on the OS clipboard (`Set-Clipboard -Value $text` in PowerShell, `pbcopy`/`xclip` elsewhere), click inside the editor, press `ctrl+a`, then `ctrl+v`. Only as last resort type **minified single-line** text after `ctrl+a` + `Delete`.

## 4. Verify before moving on

1. Re-read `editor.getValue()` and compare with what you intended; for JSON run `JSON.parse` on it.
2. Check the page's own validation: gutter `.ace_gutter-cell.ace_error`, `editor.session.getAnnotations()`, and app linters.
3. Take a screenshot only to confirm the UI state (error banners, disabled buttons), never as the source of the text.

## AWS console policy editors

- Container: `#policy-editor-container .ace_editor` (IAM/KMS "Edit policy" JSON view). Status bar shows `JSON`, linter tabs show `Security / Errors / Warnings / Suggestions`.
- "Fix all syntax errors to view this panel." and `Errors: N > 0` mean the JSON is invalid — typical after keyboard typing: unquoted keys/values (`Effect: Allow`), stray chars (`aaAllow`, a letter inside the 12-digit account ID).
- Policy JSON must be strict: double-quoted keys and strings, `"Version": "2012-10-17"`, account IDs are 12 digits, no trailing commas.
- KMS key policies: keep the root statement (`"Principal": {"AWS": "arn:aws:iam::<account>:root"}`, `"Action": "kms:*"`) unless the user explicitly wants otherwise — removing it can make the key unmanageable.
- Wait for `Errors: 0` before the user saves. Clicking **Save changes / Next / Create** changes real infrastructure: confirm with the user first.

## Not Ace?

- `.monaco-editor` → Monaco: if `window.monaco` exists, `monaco.editor.getModels()[0].setValue(text)`.
- `.CodeMirror` → CodeMirror 5: `el.CodeMirror.setValue(text)`.
- `.cm-editor` → CodeMirror 6: needs the `EditorView` instance (`EditorView.findFromDOM(el)` when the module is reachable); otherwise use the paste fallback from section 3 on `.cm-content`.
