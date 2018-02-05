// @flow
import debug from 'debug';

const logger = debug('microfinance:log');

if (__ENV__ !== 'production') {
  debug.enable('microfinance:log');
  logger('Logging enabled!');
} else {
  debug.disable();
}

export default logger;
