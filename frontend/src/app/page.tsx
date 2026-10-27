'use client';

import { useState } from 'react';
import ParameterForm, { Params } from '../components/ParameterForm';
import ValidationStatus, { ValidationResult } from '../components/ValidationStatus';
import PolynomialList, { GenerateResult } from '../components/PolynomialList';
import CryptoPanel from '../components/CryptoPanel';
import RoundTripResult, { TestResult } from '../components/RoundTripResult';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export default function Home() {
  const [params, setParams] = useState<Params>({
    field_order: 13, eta: 2, mu: 2, degree: 3, lam1: 2, lam2: 3,
  });

  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [polys, setPolys] = useState<GenerateResult | null>(null);
  const [test, setTest] = useState<TestResult | null>(null);
  
  const [yInput, setYInput] = useState('');
  const [encResult, setEncResult] = useState<number[] | null>(null);
  const [decResult, setDecResult] = useState<number[] | null>(null);
  
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function call<T>(path: string, body: unknown): Promise<T> {
    const res = await fetch(`${API_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      const d = data?.detail;
      throw new Error(typeof d === 'string' ? d : (d?.message ?? `HTTP ${res.status}`));
    }
    return data as T;
  }

  const wrap = async (name: string, fn: () => Promise<void>) => {
    setLoading(name); setError(null);
    try { await fn(); }
    catch (e) { setError(e instanceof Error ? e.message : String(e)); }
    finally { setLoading(null); }
  };

  const doValidate = () => wrap('validate', async () => {
    setValidation(await call<ValidationResult>('/api/validate', params));
  });
  
  const doGenerate = () => wrap('generate', async () => {
    setPolys(await call<GenerateResult>('/api/generate', params));
  });
  
  const doTest = () => wrap('test', async () => {
    setTest(await call<TestResult>('/api/test', params));
  });
  
  const doEncrypt = (xStr: string) => wrap('encrypt', async () => {
    const X = xStr.split(',').map(s => Number(s.trim())).filter(n => Number.isFinite(n));
    const r = await call<{ Y: number[] }>('/api/encrypt', { ...params, X });
    setEncResult(r.Y);
    setYInput(r.Y.join(', '));
    setDecResult(null);
  });
  
  const doDecrypt = (yStr: string) => wrap('decrypt', async () => {
    const Y = yStr.split(',').map(s => Number(s.trim())).filter(n => Number.isFinite(n));
    const r = await call<{ X: number[] }>('/api/decrypt', { ...params, Y });
    setDecResult(r.X);
  });

  return (
    <main className="container">
      <header className="header">
        <h1>Каскадная символьная схема</h1>
        <p>Генератор открытого ключа и калькулятор шифрования</p>
      </header>

      {error && <div className="error-banner"><strong>Ошибка:</strong> {error}</div>}

      <ParameterForm 
        params={params} setParams={setParams} 
        onValidate={doValidate} onGenerate={doGenerate} onTest={doTest} 
        loading={loading} 
      />

      {validation && <ValidationStatus validation={validation} />}
      {polys && <PolynomialList data={polys} />}

      <CryptoPanel 
        fieldOrder={params.field_order} 
        expectedLength={params.eta * params.mu}
        onEncrypt={doEncrypt} 
        onDecrypt={doDecrypt}
        encResult={encResult}
        decResult={decResult}
        loading={loading}
        yValue={yInput}
        onUpdateY={setYInput}
      />

      {test && <RoundTripResult test={test} />}
      
      <footer style={{ textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-muted)', padding: '40px 0 20px' }}>
        Постквантовая криптография · FastAPI + Next.js (Pure CSS)
      </footer>
    </main>
  );
}