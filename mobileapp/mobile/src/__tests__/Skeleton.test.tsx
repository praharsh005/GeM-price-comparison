import React from 'react';
import { render } from '@testing-library/react-native';
import { Skeleton } from '@/components/Skeleton';

describe('Skeleton', () => {
  it('renders without crashing', () => {
    const { toJSON } = render(<Skeleton />);
    expect(toJSON()).toBeTruthy();
  });

  it('applies custom style', () => {
    const { toJSON } = render(
      <Skeleton style={{ width: 100, height: 20 }} />,
    );
    const tree = toJSON();
    expect(tree).toBeTruthy();
    if (tree && typeof tree === 'object' && 'props' in tree) {
      // In jsdom/react-native-web, numeric styles are converted to "100px" strings
      expect(tree.props.style.width).toBe('100px');
      expect(tree.props.style.height).toBe('20px');
    }
  });
});