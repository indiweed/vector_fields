'use client';

export interface Check { name: string; ok: boolean; detail: string; warning?: boolean }
export interface ValidationResult { valid: boolean; checks: Check[] }

export default function ValidationStatus({ validation }: { validation: ValidationResult }) {
  return (
    <section className="card">
      <h2>
        Результат проверки:{' '}
        <span style={{ color: validation.valid ? 'var(--success)' : 'var(--danger)', fontSize: '1rem' }}>
          {validation.valid ? 'Параметры корректны' : 'Есть ошибки'}
        </span>
      </h2>
      <ul className="check-list">
        {validation.checks.map((c, i) => {
          const type = c.warning ? 'warn' : c.ok ? 'ok' : 'err';
          return (
            <li key={i} className={`check-item ${type}`}>
              <span style={{ fontSize: '1.2rem' }}>{c.warning ? '⚠️' : c.ok ? '✅' : '❌'}</span>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{c.name}</div>
                <div style={{ fontSize: '0.8rem', opacity: 0.8 }}>{c.detail}</div>
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}