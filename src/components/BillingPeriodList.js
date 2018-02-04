import React, { Component } from 'react';
import PropTypes from 'prop-types';
import injectSheet from 'react-jss';

const styles = {
  message: {
    height: 80,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fafbfc',
  },
  row: {
    cursor: 'pointer',
  },
};

const NO_OF_PERIODS = 5;

class BillingPeriodList extends Component {
  state = { loading: true };
  componentDidMount() {
    this.fetch_periods();
  }
  componentDidUpdate(prevProps) {
    if (prevProps.date !== this.props.date) {
      this.fetch_periods();
    }
  }
  async fetch_periods() {
    try {
      const { loan, date } = this.props;
      this.setState({ loading: true });
      const { message: periods } = await frappe.call({
        method:
          'microfinance.microfinance_loan.doctype.loan.loan.get_billing_periods',
        args: {
          loan,
          interval_date: date || this.state.date,
          no_of_periods: NO_OF_PERIODS,
        },
      });
      this.setState({ periods });
    } catch (e) {
      frappe.throw(e.toString());
    } finally {
      this.setState({ loading: false });
    }
  }
  render() {
    const { classes } = this.props;
    const { loading, periods = [] } = this.state;
    if (loading) {
      return <div className={classes.message}>Loading...</div>;
    }
    if (periods.length === 0) {
      return <div className={classes.message}>No more periods.</div>;
    }
    return (
      <table className="table table-condensed table-striped table-hover">
        <thead>
          <tr>
            <th scope="col">Period</th>
            <th scope="col" className="text-right">
              Interest
            </th>
          </tr>
        </thead>
        <tbody>
          {periods.map(({ start_date, end_date, interest, as_text }) => (
            <tr
              key={as_text}
              className={classes.row}
              onClick={() => {
                this.props.on_select({ period: as_text, interest });
              }}
            >
              <td>
                {`${frappe.datetime.str_to_user(
                  start_date
                )} - ${frappe.datetime.str_to_user(end_date)} (${moment(
                  start_date
                ).format('MMM, YYYY')})`}
              </td>
              <td className="text-right">
                {format_currency(
                  interest,
                  frappe.defaults.get_default('currency'),
                  2
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    );
  }
}

export default injectSheet(styles)(BillingPeriodList);
