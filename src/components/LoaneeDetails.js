import React from 'react';
import { render } from 'react-dom';
import injectSheet from 'react-jss';

import logger from '../utils/logger';

const styles = {
  container: {
    backgroundColor: '#fafbfc',
    border: '1px solid #d1d8dd',
    borderRadius: 3,
    fontSize: 12,
    '& dl': {
      display: 'flex',
      flexFlow: 'row wrap',
      padding: '6px 12px',
    },
    '& div': {
      margin: '6px 0',
      width: '100%',
      '@media screen and (min-width: 768px)': {
        width: '50%',
      },
    },
    '& button': {
      margin: '0 12px 12px',
    },
  },
};

const LoaneeDetails = injectSheet(styles)(
  ({
    classes,
    name,
    department,
    designation,
    posting,
    date_of_joining,
    date_of_retirement,
    net_salary_amount,
    on_add,
    on_edit,
  }) => {
    if (name) {
      return (
        <div className={classes.container}>
          <dl>
            {department && (
              <div>
                <dt>Department</dt>
                <dd>{department}</dd>
              </div>
            )}
            {designation && (
              <div>
                <dt>Designation</dt>
                <dd>{designation}</dd>
              </div>
            )}
            {posting && (
              <div>
                <dt>Posting</dt>
                <dd>{posting}</dd>
              </div>
            )}
            {date_of_joining && (
              <div>
                <dt>Date of Joining</dt>
                <dd>{frappe.datetime.str_to_user(date_of_joining)}</dd>
              </div>
            )}
            {date_of_retirement && (
              <div>
                <dt>Date of Retirement</dt>
                <dd>{frappe.datetime.str_to_user(date_of_retirement)}</dd>
              </div>
            )}
            {net_salary_amount && (
              <div>
                <dt>Net Salary Amount</dt>
                <dd>
                  {format_currency(
                    net_salary_amount,
                    frappe.defaults.get_default('currency'),
                    2
                  )}
                </dd>
              </div>
            )}
          </dl>
          <button className="btn btn-default btn-xs" onClick={on_edit}>
            Edit
          </button>
        </div>
      );
    }
    return (
      <div>
        <p className="text-muted small">No details yet.</p>
        <button className="btn btn-xs btn-default" onClick={on_add}>
          Add Details
        </button>
      </div>
    );
  }
);

export default function(node, props) {
  render(<LoaneeDetails {...props} />, node);
  logger('LoaneeDetails mounted');
}
