"""obtune — Does fine-tuning teach semantic invariance under code obfuscation?

LoRA-tunes LLMs on output prediction over still-obfuscated code (never
deobfuscation) and measures transfer across obfuscation conditions, languages,
and a held-out obfuscator (H1). See CLAUDE.md for the charter and
docs/design_doc_v0.1.md for the full design.
"""

__version__ = "0.1.0"
