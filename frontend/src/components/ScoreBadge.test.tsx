import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { ScoreBadge } from './ScoreBadge';

describe('ScoreBadge Component', () => {
  it('renders Excellent Match for scores >= 85', () => {
    render(<ScoreBadge score={92} />);
    expect(screen.getByText('92%')).toBeDefined();
    expect(screen.getByText('(Excellent Match)')).toBeDefined();
  });

  it('renders Strong Match for scores between 70 and 84', () => {
    render(<ScoreBadge score={76} />);
    expect(screen.getByText('76%')).toBeDefined();
    expect(screen.getByText('(Strong Match)')).toBeDefined();
  });

  it('renders Potential Match for scores between 55 and 69', () => {
    render(<ScoreBadge score={62} />);
    expect(screen.getByText('62%')).toBeDefined();
    expect(screen.getByText('(Potential Match)')).toBeDefined();
  });

  it('renders Low Match for scores < 55', () => {
    render(<ScoreBadge score={45} />);
    expect(screen.getByText('45%')).toBeDefined();
    expect(screen.getByText('(Low Match)')).toBeDefined();
  });

  it('handles null score gracefully', () => {
    render(<ScoreBadge score={null} />);
    expect(screen.getByText('Not calculated')).toBeDefined();
  });
});

