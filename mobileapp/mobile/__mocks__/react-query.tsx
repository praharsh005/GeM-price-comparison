export const useQuery = ({ queryFn }: Record<string, any>) => ({
  data: undefined,
  isFetching: false,
  isError: false,
  error: null,
  refetch: jest.fn(),
});

export const useMutation = () => ({
  mutate: jest.fn(),
  mutateAsync: jest.fn(),
  isPending: false,
  isError: false,
  isSuccess: false,
  error: null,
});

export const QueryClient = jest.fn().mockImplementation(() => ({
  getQueryCache: jest.fn(),
  getMutationCache: jest.fn(),
  mount: jest.fn(),
  unmount: jest.fn(),
}));

export const QueryClientProvider = ({ children }: { children: React.ReactNode }) => <>{children}</>;