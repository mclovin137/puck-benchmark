import {test} from 'node:test';
import assert from 'node:assert/strict';
import {decimal,money} from '../src/money.ts';
test('preserva centavos no limite monetário sem conversão binária',()=>{
 assert.equal(decimal('99999999999999,99'),'99999999999999.99');
 assert.equal(money('99999999999999.99'),'R$ 99.999.999.999.999,99');
 assert.equal(money('-0.01'),'−R$ 0,01');
 assert.equal(money('0.10'),'R$ 0,10');
});
test('valida centavos e impede valores nulos, negativos ou fora da precisão',()=>{
 for(const value of ['0','0.00','-1','0.001','100000000000000.00','1e2','NaN','Infinity','']) assert.throws(()=>decimal(value),Error);
 assert.equal(decimal(' 0,01 '),'0.01');
 assert.equal(decimal('123.4'),'123.4');
});
