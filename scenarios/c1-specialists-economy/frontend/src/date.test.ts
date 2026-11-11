import { describe, expect, it } from 'vitest';
import { localDateISO } from './date';

describe('localDateISO', () => {
  it('usa os componentes de calendário locais sem conversão UTC', () => {
    const date = new Date(2026, 10, 5, 23, 30);
    expect(localDateISO(date)).toBe('2026-11-05');
  });
});
