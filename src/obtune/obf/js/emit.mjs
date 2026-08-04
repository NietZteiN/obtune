// The canonical JavaScript source-emission contract — ONE definition, used by every
// condition including L0.
//
// WHY this file exists: L0 normalization and the L1r/L2/L1b/S1/S2 transforms both
// round-trip source through Babel, and if they print it differently then an
// identifier condition differs from its L0 parent in *whitespace as well as
// identifiers*. That would confound the manipulation (and make the JS L0-vs-L1b
// contrast not equivalent to the Python one, breaking the cross-language claim).
// It was a real defect: the normalizer emitted 4-space indentation with a trailing
// newline while the transforms emitted Babel's raw 2-space and no trailing newline,
// so every JS identifier variant failed the gate's `purity_line_count` check.
//
// Babel's generator dropped its `indent` option, so 4-space indentation is produced
// by doubling the leading space run — exact and level-preserving, because Babel always
// emits exactly two spaces per nesting level and never tabs. Lines inside template
// literals are protected: there, leading whitespace is part of the string value.

/** 1-based line numbers whose leading whitespace is significant (template literals). */
export function protectedLines(ast, parse, code) {
  const lines = new Set();
  const tree = ast ?? parse(code);
  const walk = (node) => {
    if (!node || typeof node !== 'object') return;
    if (Array.isArray(node)) {
      node.forEach(walk);
      return;
    }
    if (node.type === 'TemplateLiteral' && node.loc) {
      for (let l = node.loc.start.line + 1; l <= node.loc.end.line; l++) lines.add(l);
    }
    for (const k of Object.keys(node)) {
      if (k === 'loc' || k === 'leadingComments' || k === 'trailingComments') continue;
      walk(node[k]);
    }
  };
  walk(tree.program ?? tree);
  return lines;
}

/** Widen Babel's 2-space indentation to 4, skipping protected lines. */
export function widenIndent(code, protectedSet) {
  return code
    .split('\n')
    .map((line, i) => {
      if (protectedSet.has(i + 1)) return line;
      const m = /^( *)(.*)$/.exec(line);
      return ' '.repeat(m[1].length * 2) + m[2].replace(/\s+$/, '');
    })
    .join('\n');
}

export const GENERATE_OPTS = {
  comments: false,
  retainLines: false,
  concise: false,
  compact: false,
};

/**
 * Print an AST in obtune-canonical form: no comments, 4-space indentation, no blank
 * lines, exactly one trailing newline.
 *
 * `generate` and `parse` are injected so this module stays free of a hard Babel
 * dependency and both callers can pass their own already-resolved bindings.
 */
export function emit(ast, generate, parse) {
  const printed = generate(ast, GENERATE_OPTS).code;
  const prot = protectedLines(null, parse, printed);
  const widened = widenIndent(printed, prot);
  const kept = widened.split('\n').filter((line, i) => prot.has(i + 1) || line.trim() !== '');
  return kept.join('\n') + (kept.length ? '\n' : '');
}
