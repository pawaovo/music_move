// @ts-nocheck

export function cn(...classNames: any[]) {
  return classNames.filter(Boolean).join(' ')
}
