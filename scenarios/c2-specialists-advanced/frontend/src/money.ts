/** Formatação decimal sem converter valores financeiros a ponto flutuante. */
export function money(value: string): string {
  const negative = value.startsWith('-');
  const [whole, fraction = ''] = value.replace(/^-/, '').split('.');
  return `${negative ? '−' : ''}R$ ${whole.replace(/\B(?=(\d{3})+(?!\d))/g, '.')},${fraction.padEnd(2, '0')}`;
}
export function decimal(value: string): string {
  const normalized = value.trim().replace(',', '.');
  if (!/^\d{1,14}(\.\d{1,2})?$/.test(normalized) || !/[1-9]/.test(normalized)) throw new Error('Informe um valor maior que zero, com até 14 inteiros e 2 decimais.');
  return normalized;
}
