import React from 'react';
import { render } from 'react-dom';

import logger from './utils/logger';
import App from './components/App';

// Enable LiveReload
if (__ENV__ !== 'production') {
  const script = document.createElement('script');
  script.src = `http://${
    (location.host || 'localhost').split(':')[0]
  }:35729/livereload.js?snipver=1`;
  document.body.appendChild(script);
}

export function CalculatePrincipal(node) {
  render(<App />, node);
  logger('Component mounted.');
  return { date: Date.now() };
}
