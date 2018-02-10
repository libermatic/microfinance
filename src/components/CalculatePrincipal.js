// @flow
import React, { Component } from 'react';
import { render } from 'react-dom';
import injectSheet from 'react-jss';

import logger from '../utils/logger';
import FieldGroup from './FieldGroup';
import Field from './Field';
import CalculatePrincipalResult from './CalculatePrincipalResult';
import type { CalculatePrincipalResultDataProps } from './CalculatePrincipalResult';
import { ui } from './styles';

const styles = {
  actions: {
    padding: '0 15px 15px',
    [ui.breakpointMd]: {
      padding: '0 30px 15px',
    },
    '& > button': {
      margin: '0 6px',
    },
    '& > button:first-of-type': {
      marginLeft: 0,
    },
    '& > button:last-of-type': {
      marginRight: 0,
    },
  },
  result: {
    margin: '15px 15px',
    [ui.breakpointMd]: {
      margin: '15px 30px',
    },
  },
};

type Props = {
  classes: any,
};
type State = {
  loading: boolean,
  params: {
    income?: number,
    date_of_retirement?: string,
    loan_plan?: string,
  },
  result: CalculatePrincipalResultDataProps,
};

class CalculatePrincipal extends Component<Props, State> {
  state: State = { loading: false, params: {}, result: {} };
  handleCalculate = async () => {
    const { params } = this.state;
    if (!params.income || !params.date_of_retirement || !params.loan_plan) {
      return frappe.throw('Values cannot be empty');
    }
    try {
      const { income, date_of_retirement: end_date, loan_plan } = params;
      this.setState({ loading: true });
      const { message: result } = await frappe.call({
        method:
          'microfinance.microfinance_loan.api.calculate_principal_and_duration.execute',
        args: { income, end_date, loan_plan },
      });
      this.setState({ result });
    } finally {
      this.setState({ loading: false });
    }
  };
  handleReset = () => {
    this.setState({ params: {}, result: {} });
  };
  render() {
    const { classes } = this.props;
    const { loading, params, result } = this.state;
    return (
      <div>
        <FieldGroup
          onChange={state => this.setState({ params: { ...params, ...state } })}
        >
          <Field label="Income" fieldtype="Currency" value={params.income} />
          <Field
            label="Date of Retirement"
            fieldtype="Date"
            value={params.date_of_retirement}
          />
          <Field fieldtype="Column Break" />
          <Field
            label="Loan Plan"
            fieldtype="Link"
            options="Loan Plan"
            value={params.loan_plan}
          />
        </FieldGroup>
        <div className={classes.actions}>
          <button className="btn btn-primary" onClick={this.handleCalculate}>
            Calculate
          </button>
          <button className="btn" onClick={this.handleReset}>
            Reset
          </button>
        </div>
        <CalculatePrincipalResult
          className={classes.result}
          {...result}
          loading={loading}
        />
      </div>
    );
  }
}

const CalculatePrincipalStyled = injectSheet(styles)(CalculatePrincipal);

export default function(node: HTMLDivElement) {
  render(<CalculatePrincipalStyled />, node);
  logger('CalculatePrincipal mounted');
}
