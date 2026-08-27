import { describe, it, expect } from 'vitest'
import { getSeason } from './season'

describe('getSeason', () => {
  it('returns Winter for late February', () => {
    const winterDate= new Date(2026, 1, 28)
    expect(getSeason(winterDate)).toBe("Winter")
  })

  it('returns Spring for early March', () => {
    const springDate = new Date(2026, 4, 1)
    expect(getSeason(springDate)).toBe("Spring")
  })
})