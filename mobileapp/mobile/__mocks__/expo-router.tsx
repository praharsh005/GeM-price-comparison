import React from 'react';
import { Pressable } from 'react-native';

export const useLocalSearchParams = () => ({});

export const useRouter = () => ({
  push: jest.fn(),
  replace: jest.fn(),
  back: jest.fn(),
});

export const Link = ({ children, asChild, ...props }: { children: React.ReactNode; asChild?: boolean; onPress?: () => void; href?: string; [key: string]: any }) => {
  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children, { ...props, onPress: jest.fn() } as React.ComponentProps<typeof Pressable>);
  }
  return <Pressable {...props} onPress={jest.fn()}>{children}</Pressable>;
};

export const Stack = ({ children }: { children: React.ReactNode }) => <>{children}</>;
export const Tabs = ({ children }: { children: React.ReactNode }) => <>{children}</>;