# AWS console policy editors (Ace)

The JSON policy editors in the AWS console — IAM policies, KMS key policies, S3 bucket policies, Organizations SCPs, resource-based policies — are Ace editors wrapped in a Cloudscape "cloud editor". Use the generic method from `SKILL.md` (find the editor, replace the whole document through the API, verify); this file only adds what is specific to AWS.

## Recognising it

- Status bar shows the language (`JSON`) and the cursor position (`11:18`).
- A policy linter under the editor with tabs `Security`, `Errors`, `Warnings`, `Suggestions`.
- In IAM/KMS the side panel shows "Fix all syntax errors to view this panel." while the JSON is invalid.
- The DOM id of the wrapper (e.g. `#policy-editor-container`) is an implementation detail — select the editor with the finder in `SKILL.md` (visible, JSON mode, label/position) instead of relying on it.

## Editing workflow

1. Read the current policy with `editor.getValue()` and `JSON.parse` it. If parsing fails, the document is already broken — ask the user what it should contain instead of guessing.
2. Change the parsed object, not the text.
3. Serialize with the editor's indentation: `JSON.stringify(policy, null, editor.session.getTabString())`.
4. `editor.setValue(text, -1)`.
5. Verify: `JSON.parse(editor.getValue())` succeeds, the linter shows `Errors: 0`, and the side panel is back.
6. Saving (**Save changes**, **Next**, **Create policy**) changes real infrastructure — confirm with the user before clicking.

## Typical corruption after keyboard typing

- Unquoted keys or values: `Effect: Allow`.
- Stray or duplicated characters: `aaAllow`, letters inside the 12-digit account ID.
- Doubled indentation and extra closing brackets from auto-indent and auto-pairing.

Rebuild the document from a parsed object rather than patching those by hand.

## Policy rules worth checking

- Strict JSON: double-quoted keys and strings, no comments, no trailing commas.
- `"Version": "2012-10-17"`.
- `Principal` ARNs use a 12-digit account ID: `arn:aws:iam::<account-id>:root`.
- KMS key policies: keep the statement that grants the account root `kms:*` unless the user explicitly wants otherwise — removing it can make the key unmanageable.
- Size limits (check current AWS quotas): IAM managed policy 6,144 characters, inline policy 2,048 (user) / 5,120 (group) / 10,240 (role), SCP 5,120 characters, KMS key policy 32 KB, S3 bucket policy 20 KB. Whitespace counts toward some of these limits — compact the JSON if the linter reports size errors.
