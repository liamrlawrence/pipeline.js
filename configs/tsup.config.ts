import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['static/ts/**/*.ts'],
  format: ['esm'],
  external: [],
  splitting: false,
  sourcemap: true,
  clean: true,
  outDir: 'static/dist',
  noExternal: []
});

