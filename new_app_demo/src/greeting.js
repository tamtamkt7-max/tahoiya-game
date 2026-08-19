export function greet(name) {
  const normalized = String(name ?? '').trim();
  return `Hello, ${normalized || 'guest'}!`;
}
