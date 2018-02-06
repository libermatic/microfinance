// @flow
import React, { Component } from 'react';
import { render } from 'react-dom';
import injectSheet from 'react-jss';

import logger from '../utils/logger';
import BillingPeriodList from './BillingPeriodList';
import type { Props } from './BillingPeriodList';

const styles = {
  actions: {
    display: 'flex',
    justifyContent: 'space-between',
  },
};

const NO_OF_PERIODS = 5;

type State = {
  date: string,
};

class BillingPeriodDialog extends Component<Props, State> {
  state = { date: this.props.date || frappe.datetime.nowdate() };
  render() {
    const { classes } = this.props;
    return (
      <div>
        <div className={classes.actions}>
          <div className="btn-group">
            <button
              className="btn btn-info"
              onClick={() => {
                this.setState({
                  date: frappe.datetime.add_months(
                    this.state.date,
                    -NO_OF_PERIODS
                  ),
                });
              }}
            >
              <i className="octicon octicon-chevron-left" /> Previous
            </button>
            <button
              className="btn btn-info"
              onClick={() => {
                this.setState({ date: frappe.datetime.nowdate() });
              }}
            >
              Current
            </button>
            <button
              className="btn btn-info"
              onClick={() => {
                this.setState({
                  date: frappe.datetime.add_months(
                    this.state.date,
                    NO_OF_PERIODS
                  ),
                });
              }}
            >
              Next <i className="octicon octicon-chevron-right" />
            </button>
          </div>
          <button
            className="btn btn-danger"
            onClick={() => {
              this.props.on_select({});
            }}
          >
            None
          </button>
        </div>
        <BillingPeriodList {...this.props} date={this.state.date} />
      </div>
    );
  }
}
const BillingPeriodDialogStyled = injectSheet(styles)(BillingPeriodDialog);

export default function(node: HTMLDivElement, props: Props) {
  render(<BillingPeriodDialogStyled {...props} />, node);
  logger('BillingPeriodDialog mounted');
}
