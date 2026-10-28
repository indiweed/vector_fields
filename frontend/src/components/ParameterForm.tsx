'use client';

export interface Params {
  field_order: number; eta: number; mu: number;
  degree: number; lam1: number; lam2: number;
}

interface Props {
  params: Params;
  setParams: (p: Params) => void;
  onValidate: () => void;
  onGenerate: () => void;
  onTest: () => void;
  loading: string | null;
}

const PRESETS = [
  { name: 'GF(13), η=2, μ=2, k=3', values: { field_order: 13, eta: 2, mu: 2, degree: 3, lam1: 2, lam2: 3 } },
  { name: 'GF(2^4), η=2, μ=2, k=3', values: { field_order: 16, eta: 2, mu: 2, degree: 3, lam1: 2, lam2: 3 } },
  { name: 'GF(2^3), η=3, μ=3, k=3', values: { field_order: 8, eta: 3, mu: 3, degree: 3, lam1: 2, lam2: 3 } },
];

export default function ParameterForm({ params, setParams, onValidate, onGenerate, onTest, loading }: Props) {
  const num = (key: keyof Params, label: string, hint?: string) => (
    <div className="input-group">
      <label>{label}</label>
      <input
        type="number" min={1}
        value={params[key]}
        onChange={e => setParams({ ...params, [key]: Number(e.target.value) })}
      />
      {hint && <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>{hint}</p>}
    </div>
  );

  return (
    <section className="card">
      <h2>⚙️ Параметры схемы</h2>
      
      <div className="presets-container">
        <span style={{ fontSize: '0.85rem', width: '100%', marginBottom: '8px', color: 'var(--text-muted)' }}>Пресеты из статьи:</span>
        {PRESETS.map((preset, i) => (
          <button key={i} onClick={() => setParams(preset.values)} className="preset-btn">
            {preset.name}
          </button>
        ))}
      </div>

      <div className="grid-params">
        {num('field_order', 'Порядок поля q', '13 → GF(13); 16 → GF(2⁴)')}
        {num('eta', 'η (1-й слой)')}
        {num('mu', 'μ (2-й слой)')}
        {num('degree', 'Степень k')}
        {num('lam1', 'λ₁ (лямбда 1)')}
        {num('lam2', 'λ₂ (лямбда 2)')}
      </div>

      <div className="btn-actions">
        <button onClick={onValidate} disabled={!!loading} className="btn btn-dark">
          {loading === 'validate' ? 'Проверка…' : 'Проверить параметры'}
        </button>
        <button onClick={onGenerate} disabled={!!loading} className="btn btn-primary">
          {loading === 'generate' ? 'Генерация…' : 'Сгенерировать ключ'}
        </button>
        <button onClick={onTest} disabled={!!loading} className="btn btn-success">
          {loading === 'test' ? 'Тест…' : 'Тест обратимости'}
        </button>
      </div>
    </section>
  );
}