// @flow
import React, { Component } from 'react';
import { render } from 'react-dom';
import injectSheet from 'react-jss';

import logger from '../utils/logger';
import FieldGroup from './FieldGroup';
import Field from './Field';
import LateChargesList from './LateChargesList';
import LateChargesListItem from './LateChargesListItem';
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
    loan?: string,
  },
  result: Array<any>,
};

class LateChargesTool extends Component<Props, State> {
  state: State = { loading: false, params: {}, result: [] };
  handleCalculate = async () => {
    const { params } = this.state;
    if (!params.loan) {
      return frappe.throw('Value cannot be empty');
    }
    try {
      const { loan } = params;
      this.setState({ loading: true });
      const { message: result } = await frappe.call({
        method: 'microfinance.microfinance_loan.api.interests_and_charges.list',
        args: { loan },
      });
      this.setState({ result });
    } finally {
      this.setState({ loading: false });
    }
  };
  handleReset = () => {
    this.setState({ params: {}, result: [] });
  };
  render() {
    const { classes } = this.props;
    const { loading, params, result } = this.state;
    return (
      <div>
        <FieldGroup
          onChange={state => this.setState({ params: { ...params, ...state } })}
        >
          <Field
            label="Loan"
            fieldtype="Link"
            options="Loan"
            value={params.loan}
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
        <LateChargesList>
          {result.map(item => <LateChargesListItem {...item} />)}
        </LateChargesList>
      </div>
    );
  }
}

const LateChargesToolStyled = injectSheet(styles)(LateChargesTool);

export default function(node: HTMLDivElement) {
  render(<LateChargesToolStyled />, node);
  logger('LateChargesTool mounted');
}
