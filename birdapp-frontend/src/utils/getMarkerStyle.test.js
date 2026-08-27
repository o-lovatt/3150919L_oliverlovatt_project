import { describe, it, expect } from 'vitest'
import { getMarkerStyle } from './markerStyle'


describe('getMarkerStyle', () => {
  it('does not crash when maxScore is 0', () => {
    const result = getMarkerStyle(0, 0)
    expect(result.radius).toBeGreaterThan(0)
    expect(result.color).toBeDefined()
  })

  it('gives the highest colour intensity when score equals maxScore', () => {
    const result = getMarkerStyle(10, 10)
    expect(result.radius).toBe(10)
    expect(result.color).toBe("rgb(15, 82, 186)")
  })
})
