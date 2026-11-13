import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
for(const viewport of [{width:1280,height:900},{width:360,height:800}]){
 test(`jornada e acessibilidade ${viewport.width}`,async({page},info)=>{
  await page.setViewportSize(viewport);await page.goto('/');
  await expect(page.getByRole('heading',{name:'Bom ter você aqui'})).toBeVisible();
  await expect(page.locator('html')).toHaveAttribute('lang','pt-BR');
  await page.getByRole('button',{name:'Criar conta',exact:true}).click();
  await page.getByLabel('Nome',{exact:true}).fill('Pessoa C4');await page.getByLabel('E-mail',{exact:true}).fill(`ui${viewport.width}-${Date.now()}@example.test`);await page.getByLabel('Senha',{exact:true}).fill('a-long-example-password');
  await page.getByRole('button',{name:'Criar conta',exact:true}).click();await expect(page.getByRole('heading',{name:'Olá, Pessoa.'})).toBeVisible();await expect(page.getByText('Nenhuma movimentação por aqui')).toBeVisible();
  await page.getByRole('button',{name:'Nova movimentação',exact:false}).click();
  const dialog=page.getByRole('dialog');await dialog.getByLabel('Tipo',{exact:true}).selectOption('INCOME');await dialog.getByLabel('Descrição',{exact:true}).fill('Salário UI');await dialog.getByLabel('Categoria',{exact:true}).fill('Trabalho');await dialog.getByLabel('Valor (R$)',{exact:true}).fill('1234.56');await dialog.getByLabel('Data',{exact:true}).fill('2026-01-10');await dialog.getByRole('button',{name:'Salvar movimentação'}).click();await expect(dialog).toHaveCount(0);
  await expect(page.getByText('Salário UI',{exact:true})).toBeVisible();await expect(page.getByText('R$ 1.234,56',{exact:true}).first()).toBeVisible();
  await page.getByRole('button',{name:'Ver Salário UI',exact:true}).click();await expect(page.getByRole('dialog').getByText('Trabalho',{exact:true})).toBeVisible();await page.keyboard.press('Escape');
  await page.getByRole('button',{name:'Editar Salário UI',exact:true}).click();await page.getByRole('dialog').getByLabel('Valor (R$)').fill('1500.01');await page.getByRole('button',{name:'Salvar movimentação'}).click();await expect(page.getByText('R$ 1.500,01',{exact:true}).first()).toBeVisible();
  await page.getByLabel('Descrição contém').fill('Salário');await page.getByRole('button',{name:'Aplicar filtros'}).click();await expect(page.getByText('1 registros encontrados')).toBeVisible();
  for(const name of ['↓ PDF','↓ Excel']){const download=page.waitForEvent('download');await page.getByRole('button',{name,exact:true}).click();expect((await download).suggestedFilename()).toMatch(/movimentacoes\.(pdf|xlsx)/);}
  const audit=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();await info.attach('axe.json',{body:JSON.stringify(audit,null,2),contentType:'application/json'});expect(audit.violations).toEqual([]);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();await page.screenshot({path:`../evidence/desktop-${viewport.width}.png`,fullPage:true});
  await page.getByLabel('Tema',{exact:true}).selectOption('2');await page.getByLabel('Modo',{exact:true}).selectOption('escuro');const darkAudit=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();await info.attach('axe-dark.json',{body:JSON.stringify(darkAudit,null,2),contentType:'application/json'});expect(darkAudit.violations).toEqual([]);await page.screenshot({path:`../evidence/dark-${viewport.width}.png`,fullPage:true});
  await page.getByRole('button',{name:'Excluir Salário UI'}).click();await page.getByRole('button',{name:'Manter registro'}).click();await expect(page.getByText('Salário UI',{exact:true})).toBeVisible();await page.getByRole('button',{name:'Excluir Salário UI'}).click();await page.getByRole('button',{name:'Confirmar exclusão'}).click();await expect(page.getByText('Nenhuma movimentação por aqui')).toBeVisible();
  await page.getByRole('button',{name:'Sair',exact:true}).click();await expect(page.getByRole('heading',{name:'Bom ter você aqui'})).toBeVisible();expect(await page.evaluate(()=>Object.keys(localStorage))).toEqual([]);
 });
}
