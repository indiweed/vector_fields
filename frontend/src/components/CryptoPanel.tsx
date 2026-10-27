'use client';
import { useState } from 'react';

interface Props {
  fieldOrder: number;
  expectedLength: number;
  onEncrypt: (x: string) => Promise<void>;
  onDecrypt: (y: string) => Promise<void>;
  encResult: number[] | null;
  decResult: number[] | null;
  loading: string | null;
  onUpdateY: (y: string) => void;
  yValue: string;
}

export default function CryptoPanel({ fieldOrder, expectedLength, onEncrypt, onDecrypt, encResult, decResult, loading, onUpdateY, yValue }: Props) {
  const [xValue, setXValue] = useState('1, 2, 3, 4');

  const generateRandomX = () => {
    const arr = Array.from({ length: expectedLength }, () => Math.floor(Math.random() * fieldOrder));
    setXValue(arr.join(', '));
  };

  return (
    <section className="crypto-grid">
      {/* Шифрование */}
      <div className="card">
        <h2 style={{ color: 'var(--primary)' }}>🔒 Шифрование</h2>
        
        <div className="input-group">
          <label>Вектор X (через запятую)</label>
          <div className="input-with-btn">
            <input
              value={xValue}
              onChange={e => setXValue(e.target.value)}
            />
            <button onClick={generateRandomX} title="Случайный вектор" className="btn btn-dark" style={{ padding: '0 12px' }}>
              🎲
            </button>
          </div>
        </div>

        <button onClick={() => onEncrypt(xValue)} disabled={!!loading} className="btn btn-primary btn-full" style={{ marginTop: '16px' }}>
          {loading === 'encrypt' ? 'Шифрование…' : 'Зашифровать →'}
        </button>

        {encResult && (
          <div className="result-box enc">
            <div style={{ fontSize: '0.75rem', fontWeight: 'bold', marginBottom: '4px', opacity: 0.7 }}>Результат Y:</div>
            [{encResult.join(', ')}]
          </div>
        )}
      </div>

      {/* Расшифрование */}
      <div className="card">
        <h2 style={{ color: 'var(--purple)' }}>🔓 Расшифрование</h2>
        
        <div className="input-group">
          <label>Вектор Y (через запятую)</label>
          <input
            value={yValue}
            onChange={e => onUpdateY(e.target.value)}
            placeholder="Вставьте Y сюда"
          />
        </div>

        <button onClick={() => onDecrypt(yValue)} disabled={!!loading || !yValue} className="btn btn-purple btn-full" style={{ marginTop: '16px' }}>
          {loading === 'decrypt' ? 'Расшифрование…' : '← Расшифровать'}
        </button>

        {decResult && (
          <div className="result-box dec">
            <div style={{ fontSize: '0.75rem', fontWeight: 'bold', marginBottom: '4px', opacity: 0.7 }}>Результат X:</div>
            [{decResult.join(', ')}]
          </div>
        )}
      </div>
    </section>
  );
}