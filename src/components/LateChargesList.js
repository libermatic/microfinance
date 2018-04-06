// @flow
import React from 'react';
import type { Element } from 'React';

import LateChargesListItem from './LateChargesListItem';

type Props = {
  children: Array<Element<typeof LateChargesListItem>>,
};

const LateChargesList = ({ children }: Props) => {
  if (!children || children.length === 0) {
    return <div>No data found.</div>;
  }
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Period</th>
          <th>Posting Date</th>
          <th>Amount</th>
          <th>Status</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>{children}</tbody>
    </table>
  );
};

export default LateChargesList;
