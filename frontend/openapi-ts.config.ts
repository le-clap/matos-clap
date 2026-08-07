import { defineConfig } from '@hey-api/openapi-ts';

export default defineConfig({
  input: '../backend/openapi.json',
  output: {
    path: 'src/client',
    postProcess: ['prettier'],
  },
  plugins: [
    '@hey-api/client-fetch',
    {
      name: '@hey-api/sdk',
      operations: {
        strategy: 'byTags',
        containerName: '{{name}}Service',
      },
    },
  ],
});
