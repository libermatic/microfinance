// @flow
import React from 'react';
import injectSheet from 'react-jss';
import classnames from 'classnames';

import { ui } from './styles';

const styles = {
  container: {
    border: ui.border,
    padding: 16,
    borderRadius: 3,
    backgroundColor: ui.canvasColorAlternate,
  },
  content: {
    display: 'flex',
    flexFlow: 'column wrap',
    padding: 8,
    [ui.breakpointMd]: {
      maxHeight: 120,
    },
    '& > div': {
      margin: 8,
    },
    '& dt': {
      fontVariant: 'all-small-caps',
      fontWeight: 'normal',
    },
    '& dd': {
      fontWeight: 'bold',
    },
  },
  zeroData: {
    backgroundColor: ui.warningColor,
  },
  main: {
    '& dd': {
      fontSize: '1.6em',
    },
  },
};

export type CalculatePrincipalResultDataProps = {
  principal?: number,
  expected_eta?: string,
  recovery_amount?: number,
  initial_interest?: number,
};

type Props = CalculatePrincipalResultDataProps & {
  className?: string,
  classes: any,
  loading: boolean,
};

const CalculatePrincipalResult = ({
  className,
  classes,
  loading,
  principal,
  expected_eta,
  recovery_amount,
  initial_interest,
}: Props) => {
  const css = classnames(className, classes.container, {
    [classes.zeroData]: principal === 0,
    [classes.content]: principal && principal !== 0,
  });
  if (loading) {
    return <div className={css}>Loading...</div>;
  }
  if (principal === 0) {
    return <div className={css}>No Loan Available</div>;
  }
  if (principal) {
    return (
      <dl className={css}>
        <div className={classes.main}>
          <dt>Max Principal</dt>
          <dd>
            {format_currency(
              principal,
              frappe.defaults.get_default('currency'),
              2
            )}
          </dd>
        </div>
        <div>
          <dt>Expected End Date</dt>
          <dd>
            {expected_eta ? frappe.datetime.str_to_user(expected_eta) : 'NA'}
          </dd>
        </div>
        <div>
          <dt>Capital Recovery Amount</dt>
          <dd>
            {recovery_amount
              ? format_currency(
                recovery_amount,
                frappe.defaults.get_default('currency'),
                2
              )
              : 'NA'}
          </dd>
        </div>
        <div>
          <dt>Initial Interest</dt>
          <dd>
            {initial_interest
              ? format_currency(
                initial_interest,
                frappe.defaults.get_default('currency'),
                2
              )
              : 'NA'}
          </dd>
        </div>
      </dl>
    );
  }
  return null;
};

export default injectSheet(styles)(CalculatePrincipalResult);
