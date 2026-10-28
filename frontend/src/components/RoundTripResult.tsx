'use client';

export interface TestResult {
  success: boolean; X: number[]; Y: number[]; X_decrypted: number[];
  encrypt_time_ms: number; decrypt_time_ms: number;
}

export default function RoundTripResult({ test }: { test: TestResult }) {
    if (!test || !test.X || !test.Y || !test.X_decrypted) {
        return (
        <section className="card">
            <h2>Результат теста: <span className="badge error">ОШИБКА</span></h2>
            <p style={{ color: 'var(--danger)' }}>Не удалось получить данные для теста. Проверьте параметры.</p>
        </section>
        );
    }

  return (
    <section className="card">
      <h2 style={{ marginBottom: '16px' }}>
        Результат теста:{' '}
        <span className={`badge ${test.success ? 'success' : 'error'}`}>
          {test.success ? 'УСПЕШНО' : 'ОШИБКА'}
        </span>
      </h2>
      
      <div className="test-grid">
        <div className="test-box">
          <div className="test-box-title">Исходный X</div>
          [{test.X.join(', ')}]
        </div>
        <div className="test-box" style={{ background: '#eff6ff', borderColor: '#bfdbfe', color: '#1e3a8a' }}>
          <div className="test-box-title" style={{ color: '#3b82f6' }}>Зашифрованный Y</div>
          [{test.Y.join(', ')}]
        </div>
        <div className="test-box" style={{ background: '#f0fdf4', borderColor: '#bbf7d0', color: '#14532d' }}>
          <div className="test-box-title" style={{ color: '#22c55e' }}>decrypt(Y)</div>
          [{test.X_decrypted.join(', ')}]
        </div>
      </div>
      
      <div style={{ display: 'flex', gap: '16px', fontSize: '0.85rem', color: 'var(--text-muted)', background: '#f1f5f9', padding: '12px', borderRadius: '8px' }}>
        <span>Шифрование: <strong style={{ color: 'var(--text-main)' }}>{test.encrypt_time_ms} мс</strong></span>
        <span>Расшифрование: <strong style={{ color: 'var(--text-main)' }}>{test.decrypt_time_ms} мс</strong></span>
      </div>
    </section>
  );
}