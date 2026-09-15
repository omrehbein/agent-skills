---
name: ace-editor
description: "Use when an agent automating a web page must find, read, replace or validate text inside an Ace code editor (elements with class `ace_editor`) — code/JSON/YAML/SQL editors embedded in cloud consoles (e.g. AWS policy editors), Cloudscape/awsui, Cloud9-style IDEs, react-ace, admin panels. Also use when text typed into a web code editor comes out mangled (extra or missing quotes/brackets, doubled indentation), when only part of a document is visible in the DOM or a screenshot, or when you need the editor's syntax errors."
---

# Ace editor automation

Ace renders only the rows on screen and receives keystrokes through a hidden `textarea` that auto-closes quotes/brackets and auto-indents new lines. Typing `{`, Enter, `    "a": [1]`, Enter, `}` into a default Ace JSON editor produces:

```text
{
        "a": [1]
}
}
```

So:

- **Read and write through the editor API** with JavaScript running in the page. Don't scrape `.ace_line` elements or screenshots for content, and don't type code key by key.
- **Run in the page's main world.** Properties the page sets on elements (such as `el.env`) are invisible from isolated worlds, e.g. browser-extension content scripts. Use your tool's main-world option, or the fallback in step 5.
- **Respect read-only editors.** The API can still change them, but the app doesn't expect it — only do it when the user asks.
- **Changing the editor is not saving.** Confirm with the user before clicking Save / Submit / Apply.

Snippets below are plain page JavaScript whose last expression is the result. Step 7 uses `await`; if your tool has no top-level `await`, wrap the snippet in an async function (e.g. Playwright `page.evaluate(async () => { ... })`).

## 1. Find the editors

Ace's renderer adds the `ace_editor` class to every editor container, in every version, so the selector is stable. What varies is *where* editors live (main document, open shadow roots, same-origin iframes), which elements are real editors (the autocomplete popup is an Ace editor too) and whether the instance is reachable. Search dynamically:

```js
(() => {
  const hits = [];
  const walk = (root, where) => {
    for (const el of root.querySelectorAll('.ace_editor')) hits.push({ el, where });
    for (const node of root.querySelectorAll('*')) {
      if (node.shadowRoot) walk(node.shadowRoot, `${where} > ${node.localName}::shadow`);
    }
    for (const frame of root.querySelectorAll('iframe, frame')) {
      let doc = null;
      try { doc = frame.contentDocument; } catch {}
      if (doc) walk(doc, `${where} > iframe${frame.id ? '#' + frame.id : ''}`);
      else hits.push({ el: null, where: `${where} > cross-origin iframe ${frame.src}` });
    }
  };
  walk(document, 'document');
  // the autocomplete popup is also an Ace editor: skip it
  const found = hits.filter(h => !h.el?.classList.contains('ace_autocomplete'));
  window.__aceEditors = found.map(h => h.el);
  return found.map(({ el, where }, i) => {
    if (!el) return { i, where, note: 'not reachable from this page: open the frame URL directly' };
    const ed = el.env?.editor;
    return {
      i,
      where,
      id: el.id || undefined,
      label: el.closest('[aria-label]')?.getAttribute('aria-label') || undefined,
      visible: el.getClientRects().length > 0,
      handle: !!ed,
      mode: ed?.session.getMode().$id,
      readOnly: ed?.getReadOnly(),
      lines: ed?.session.getLength(),
      firstLine: (ed ? ed.session.getLine(0) : el.querySelector('.ace_line')?.textContent ?? '').slice(0, 60),
    };
  });
})()
```

- Pick the target by `label`, `id`, `mode`, `firstLine`, `visible`; use its `i` in the next steps (the examples use `0`).
- Re-run the finder after navigation or re-renders. An empty list on a single-page app usually means the editor isn't mounted yet: wait and retry.
- `handle: false` → the page built the editor without `ace.edit()` (no `el.env`) or you are in an isolated world: use step 5. **Never call `ace.edit(el)` to get a handle** — on an element without `env` it creates a second editor on top of the page's one.

## 2. Inspect and read

```js
const editor = window.__aceEditors[0].env.editor; // index from the finder
({
  mode: editor.session.getMode().$id, // e.g. ace/mode/json (ace/mode/text while a mode is still loading)
  readOnly: editor.getReadOnly(),
  lines: editor.session.getLength(),
  indent: JSON.stringify(editor.session.getTabString()),
  cursor: editor.getCursorPosition(), // { row, column }, 0-based
  selection: editor.getSelectedText(),
  text: editor.getValue(),
})
```

For very large documents read slices with `editor.session.getLines(firstRow, lastRow)` (0-based, inclusive).

## 3. Replace the whole document

```js
const editor = window.__aceEditors[0].env.editor;
const newText = '...'; // the full new content
editor.session.getUndoManager().startNewGroup?.(); // keep this change as its own undo step
editor.setValue(newText, -1); // -1 puts the cursor at the start; fires 'change' so the app updates its state
editor.getValue() === newText
```

Generate structured content from data instead of writing it by hand: `JSON.stringify(data, null, editor.session.getTabString())` matches the editor's indentation.

## 4. Targeted edits

```js
const editor = window.__aceEditors[0].env.editor;
// first match; options: wrap, caseSensitive, wholeWord, regExp, backwards, range
if (editor.find('oldValue', { wrap: true, caseSensitive: true })) editor.replace('newValue');
// every match, returns the count; with regExp, $1 back-references work
const replaced = editor.replaceAll('version-$1', { needle: 'v(\\d+)', regExp: true });
// by position: rows and columns are 0-based, columns past the end of the line are clipped
editor.session.replace({ start: { row: 2, column: 0 }, end: { row: 2, column: Infinity } }, 'whole new line 3');
editor.session.insert({ row: editor.session.getLength(), column: 0 }, '\nappended line');
({ replaced, text: editor.getValue() })
```

More — cursor, selection, folding, scrolling, commands, events: [references/ace-api.md](references/ace-api.md).

## 5. No handle? Paste into the hidden textarea

```js
const el = window.__aceEditors[0]; // works with handle: false
const newText = '...';
const input = el.querySelector('textarea.ace_text-input');
const mac = /Mac|iPhone|iPad/.test(navigator.platform);
input.focus();
// select all: Ace binds Ctrl+A, or Cmd+A on Apple platforms
input.dispatchEvent(new KeyboardEvent('keydown', { key: 'a', code: 'KeyA', keyCode: 65, which: 65, ctrlKey: !mac, metaKey: mac, bubbles: true, cancelable: true }));
const data = new DataTransfer();
data.setData('text/plain', newText);
input.dispatchEvent(new ClipboardEvent('paste', { clipboardData: data, bubbles: true, cancelable: true }));
'pasted'
```

- Pasted text is inserted verbatim: no auto-pairing, no auto-indent. Read-only editors ignore it.
- Alternative with the textarea focused and everything selected: `document.execCommand('insertText', false, newText)`.
- Without JavaScript: put the text on the OS clipboard, click inside the editor, press `Ctrl+A` (`Cmd+A` on macOS), then `Ctrl+V` (`Cmd+V`).
- Without a handle you can only read rendered rows (`.ace_text-layer .ace_line`, after the next frame). For the full text, select all and copy via the OS clipboard.

## 6. If you really must type

```js
const editor = window.__aceEditors[0].env.editor;
const assists = ['behavioursEnabled', 'wrapBehavioursEnabled', 'enableAutoIndent', 'enableLiveAutocompletion', 'enableBasicAutocompletion', 'enableSnippets'];
window.__aceSavedOptions = Object.fromEntries(assists.filter(name => editor.$options[name]).map(name => [name, editor.getOption(name)]));
editor.setOptions(Object.fromEntries(Object.keys(window.__aceSavedOptions).map(name => [name, false])));
editor.focus();
window.__aceSavedOptions // restore after typing: editor.setOptions(window.__aceSavedOptions)
```

Type, then restore the options. Prefer single-line content and press `Escape` before `Enter` if a completion popup is open.

## 7. Verify

```js
const editor = window.__aceEditors[0].env.editor;
// Ace's worker reports syntax errors for modes such as JSON, JavaScript, CSS, HTML and XML
await new Promise(resolve => {
  const timer = setTimeout(resolve, 3000);
  editor.session.once('changeAnnotation', () => { clearTimeout(timer); setTimeout(resolve, 50); });
});
({ useWorker: editor.getOption('useWorker'), errors: editor.session.getAnnotations().filter(a => a.type === 'error') })
```

1. Re-read with `editor.getValue()` and compare with what you intended; for JSON also run `JSON.parse` on it.
2. `useWorker: false` means the page validates elsewhere — check its linter or error gutter (`.ace_gutter-cell.ace_error`).
3. Take a screenshot only to confirm UI state (error banners, enabled buttons), never as the source of the text.

## Site notes

- AWS console policy editors (IAM, KMS, S3, SCP): [references/aws-policy-editor.md](references/aws-policy-editor.md)

## Not Ace?

- `.monaco-editor` → Monaco: if `window.monaco` exists, `monaco.editor.getModels()[0].setValue(text)`.
- `.CodeMirror` → CodeMirror 5: `el.CodeMirror.setValue(text)`.
- `.cm-editor` → CodeMirror 6: needs the `EditorView` (`EditorView.findFromDOM(el)` when the module is reachable); otherwise use the paste fallback on `.cm-content`.
