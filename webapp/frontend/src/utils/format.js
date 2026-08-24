export function formatINR(value) {
  if (value === null || value === undefined) return '—'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(value)
}

export function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  return d.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function savingsLabel(savingsPct) {
  if (savingsPct === null || savingsPct === undefined) return null
  if (savingsPct > 0) return 'Cheaper than GeM'
  if (savingsPct < 0) return 'Costlier than GeM'
  return 'Same as GeM'
}