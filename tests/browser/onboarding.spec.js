import { test, expect } from '@playwright/test';

test('homepage explains the running application', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Welcome to the team!' })).toBeVisible();
  await expect(page.getByText('Your .NET 10 development environment is up and running.')).toBeVisible();
});

test('counter responds to interactive clicks', async ({ page }) => {
  await page.goto('/counter');
  await expect(page.getByRole('status')).toHaveText('Current count: 0');
  const increment = page.getByRole('button', { name: 'Click me' });
  await expect(increment).toBeEnabled();
  await increment.click();
  await expect(page.getByRole('status')).toHaveText('Current count: 1');
  await increment.click();
  await expect(page.getByRole('status')).toHaveText('Current count: 2');
});

test('weather navigation renders five forecasts', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('navigation').getByRole('link', { name: 'Weather' }).click();
  await expect(page.getByRole('heading', { name: 'Weather', exact: true })).toBeVisible();
  await expect(page.locator('tbody tr')).toHaveCount(5);
  for (const row of await page.locator('tbody tr').all()) {
    await expect(row.getByRole('cell')).toHaveCount(4);
    await expect(row.getByRole('cell').nth(3)).not.toBeEmpty();
  }
  await expect(page.locator('#blazor-error-ui')).not.toBeVisible();
});
