import React from 'react';

import {
  QueryClient,
  QueryClientProvider as BaseQueryClientProvider,
} from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// type SidecarConfig = {
//   reactQueryDevtools?: {
//     disabled?: boolean;
//     position?: 'bottom-right' | 'top-left' | 'top-right' | 'bottom-left';
//   };
// };

export const QueryClientProvider = ({ reactQueryDevtools, children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        // staleTime: Infinity, // when to re-fetch if stale
        // cacheTime: Infinity,
      },
    },
  });

  return (
    <BaseQueryClientProvider client={queryClient}>
      {!reactQueryDevtools?.disabled && (
        <ReactQueryDevtools
          initialIsOpen={false}
          buttonPosition={reactQueryDevtools?.position || 'bottom-right'}
        />
      )}
      {children}
    </BaseQueryClientProvider>
  );
};
