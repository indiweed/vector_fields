'use client';
import { useState } from 'react';
import Math from './Math';

export interface PolyItem { index: number; latex: string; num_terms: number }
export interface GenerateResult { polynomials: PolyItem[]; generation_time_ms: number; n: number }

export default function PolynomialList({ data }: { data: GenerateResult }) {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <section className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px' }}>
        <h2 style={{ margin: 0 }}>🛡️ Открытый ключ ({data.n} многочлена)</h2>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Сгенерировано за {data.generation_time_ms} мс</span>
      </div>
      
      <div>
        {data.polynomials.map(p => (
          <div key={p.index} className="poly-item">
            <div className="poly-header">
              <span style={{ fontWeight: 'bold', fontSize: '1rem', color: 'var(--text-main)' }}>y_{p.index} =</span>
              <span>{p.num_terms} одночленов</span>
            </div>
            
            <div className="poly-math">
              <Math latex={p.latex} />
            </div>

            <button
              onClick={() => copyToClipboard(p.latex, p.index)}
              className={`copy-btn ${copiedIndex === p.index ? 'copied' : ''}`}
            >
              {copiedIndex === p.index ? '✅ Скопировано' : '📋 Copy'}
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}