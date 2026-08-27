/*
Filename: formatLikelihood.test.js
Author: Oliver Lovatt
Date: 27-08-2026
AI Usage Declaration:
- This file contains code generated with the help of AI tools.
- Tool Used: Claude AI
- Date Generated: 18-07-2026
- AI-generated sections are marked with comments: # [AI-GENERATED]
I have reviewed, tested, and understood all AI-generated code.
*/

import { describe, it, expect } from 'vitest'
import { formatLikelihood } from './formatLikelihood'

describe('formatLikelihood', () => {
  it('rounds normal percentages to whole numbers', () => {
    expect(formatLikelihood(0.20)).toBe(20)
  })

  it('shows two decimal places for values under 1%', () => {
    expect(formatLikelihood(0.0033)).toBe("0.33")
  })
})