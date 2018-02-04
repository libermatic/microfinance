import React from 'react';
import { render } from 'react-dom';
import injectSheet from 'react-jss';

import logger from '../utils/logger';

const styles = {};

const CalculatePrincipal = injectSheet(styles)(() => (
  <div>CalculatePrincipal</div>
));

export default function(node) {
  render(<CalculatePrincipal />, node);
  logger('CalculatePrincipal mounted');
}
