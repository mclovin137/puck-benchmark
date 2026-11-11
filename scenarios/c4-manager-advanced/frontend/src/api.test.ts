import {describe,it,expect} from 'vitest';
import {money,localDate} from './api';
describe('renderização financeira sem Number',()=>{it('preserva14inteiros e centavos',()=>{expect(money('99999999999999.99')).toBe('R$ 99.999.999.999.999,99');expect(money('-0.01')).toBe('− R$ 0,01');});it('preserva data local',()=>expect(localDate('2026-01-01')).toBe('01/01/2026'));});
