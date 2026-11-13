import { describe, expect, it } from 'vitest';
import { formatMoney } from './money';

describe('formatMoney', () => {
  it('preserva centavos no formato brasileiro', () => {
    expect(formatMoney('1234.50')).toBe('R$ 1.234,50');
    expect(formatMoney('0.01')).toBe('R$ 0,01');
  });
  it('mantém precisão para valores grandes e saldo negativo', () => {
    expect(formatMoney('-12345678901234.99')).toBe('-R$ 12.345.678.901.234,99');
  });
  it('não tenta formatar dados decimais inválidos', () => {
    expect(formatMoney('1.999')).toBe('Valor inválido');
  });
});
