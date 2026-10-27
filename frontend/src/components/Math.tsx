'use client';
import katex from 'katex';
import 'katex/dist/katex.min.css';

export default function Math({ latex }: { latex: string }) {
  return (
    <span
      dangerouslySetInnerHTML={{
        __html: katex.renderToString(latex, { throwOnError: false, displayMode: false }),
      }}
    />
  );
}