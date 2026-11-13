const formatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });

/** Formata strings decimais preservando centavos sem convertê-los para ponto flutuante. */
export function formatMoney(value: string): string {
  const match = /^(-?)(\d+)(?:\.(\d{1,2}))?$/.exec(value);
  if (!match) return 'Valor inválido';
  const [, sign, whole, decimals = ''] = match;
  const integer = BigInt(whole);
  const parts = formatter.formatToParts(integer);
  const amount = parts.map(part => part.type === 'integer' ? part.value : part.type === 'group' ? part.value : part.type === 'currency' || part.type === 'literal' ? part.value : '').join('');
  return `${sign ? '-' : ''}${amount},${decimals.padEnd(2, '0')}`;
}
