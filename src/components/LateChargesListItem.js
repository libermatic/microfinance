// @flow
import React from 'react';

type Props = {
  period: string,
  posting_date: Date,
  amount: number,
  status: string,
  action: () => void,
};

const LateChargesListItem = ({
  period,
  posting_date,
  amount,
  status,
  action,
}: Props) => (
  <tr>
    <td>{period}</td>
    <td>{posting_date}</td>
    <td>{amount}</td>
    <td>{status}</td>
    <td>{action}</td>
  </tr>
);

export default LateChargesListItem;
