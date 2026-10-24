import React, { useMemo } from 'react';

/**
 * Format inline markdown tokens: **bold**, `code`, and [link](url)
 */
function formatInline(text) {
  if (!text) return null;

  // Regex pattern matching [link](url), `code`, and **bold**
  const regex = /(\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\*\*([^*]+)\*\*)/g;
  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    if (match[2] && match[3]) {
      // Link: [text](url)
      parts.push(
        <a
          key={match.index}
          href={match[3]}
          target="_blank"
          rel="noopener noreferrer"
          className="text-zinc-200 underline underline-offset-4 decoration-zinc-600 hover:decoration-zinc-300 transition-colors"
        >
          {match[2]}
        </a>
      );
    } else if (match[4]) {
      // Code: `code`
      parts.push(
        <code
          key={match.index}
          className="px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-300 font-mono text-xs"
        >
          {match[4]}
        </code>
      );
    } else if (match[5]) {
      // Bold: **bold**
      parts.push(
        <strong key={match.index} className="font-semibold text-zinc-100">
          {match[5]}
        </strong>
      );
    }

    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts;
}

/**
 * Parses markdown into structured sections and blocks.
 */
function parseMarkdownDoc(md) {
  if (!md) return [];
  const clean = md.replace(/\r\n/g, '\n').trim();
  const rawSections = clean.split(/\n\s*---\s*\n/);
  const sections = [];

  for (let i = 1; i < rawSections.length; i++) {
    const secText = rawSections[i].trim();
    if (!secText) continue;

    const lines = secText.split('\n');
    let heading = '';
    let contentStartIndex = 0;

    if (lines[0].startsWith('## ')) {
      heading = lines[0].replace(/^##\s+/, '').trim();
      contentStartIndex = 1;
    }

    const bodyText = lines.slice(contentStartIndex).join('\n').trim();
    const rawBlocks = bodyText.split(/\n\n+/);
    const blocks = [];

    for (const b of rawBlocks) {
      const trimmed = b.trim();
      if (!trimmed) continue;

      if (trimmed.startsWith('>')) {
        // Blockquote / alert notice
        const bqText = trimmed
          .split('\n')
          .map((l) => l.replace(/^>\s*/, ''))
          .join('\n')
          .trim();
        blocks.push({ type: 'blockquote', text: bqText });
      } else if (/^\d+\.\s+/.test(trimmed)) {
        // Numbered list
        const items = trimmed
          .split(/\n(?=\d+\.\s+)/)
          .map((item) => item.replace(/^\d+\.\s+/, '').trim());
        blocks.push({ type: 'ol', items });
      } else if (/^-\s+/.test(trimmed)) {
        // Bullet list
        const items = trimmed
          .split(/\n(?=-\s+)/)
          .map((item) => item.replace(/^-\s+/, '').trim());
        blocks.push({ type: 'ul', items });
      } else {
        // Standard paragraph
        blocks.push({ type: 'p', text: trimmed });
      }
    }

    sections.push({ heading, blocks });
  }

  return sections;
}

export default function MarkdownDocViewer({ markdown, id = 'document-content-body' }) {
  const sections = useMemo(() => parseMarkdownDoc(markdown), [markdown]);

  return (
    <article
      id={id}
      className="rounded-lg border border-zinc-800 bg-zinc-950/40 p-6 sm:p-8 space-y-8 text-sm text-zinc-300 leading-relaxed font-sans"
    >
      {sections.map((section, sIdx) => (
        <section key={sIdx} className="space-y-3">
          {section.heading && (
            <h2 className="text-base font-semibold text-zinc-100">
              {section.heading}
            </h2>
          )}

          {section.blocks.map((block, bIdx) => {
            if (block.type === 'blockquote') {
              return (
                <div
                  key={bIdx}
                  className="p-4 rounded-lg bg-zinc-900/60 border border-zinc-800 text-xs font-mono text-zinc-300 leading-relaxed space-y-1"
                >
                  {block.text.split('\n').map((line, lIdx) => (
                    <div key={lIdx}>{formatInline(line)}</div>
                  ))}
                </div>
              );
            }

            if (block.type === 'ol') {
              return (
                <ol key={bIdx} className="list-decimal pl-5 space-y-2 text-zinc-400">
                  {block.items.map((item, iIdx) => (
                    <li key={iIdx}>{formatInline(item)}</li>
                  ))}
                </ol>
              );
            }

            if (block.type === 'ul') {
              return (
                <ul key={bIdx} className="list-disc pl-5 space-y-2 text-zinc-400">
                  {block.items.map((item, iIdx) => (
                    <li key={iIdx}>{formatInline(item)}</li>
                  ))}
                </ul>
              );
            }

            return (
              <p key={bIdx} className="text-zinc-300 leading-relaxed">
                {formatInline(block.text)}
              </p>
            );
          })}
        </section>
      ))}
    </article>
  );
}
