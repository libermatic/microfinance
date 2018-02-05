import type Moment from './npm/moment_v2.x.x';

declare var frappe: {
  call: ({ method: string, args?: any }) => { message: any },
  throw: (msg: string) => void,
  datetime: {
    str_to_user: (val: string, only_time?: boolean) => string,
    nowdate: void => string,
    add_months: (d: string, months: number) => string,
  },
  defaults: {
    get_default: (key: string) => string,
  },
}

declare function format_currency(
  v: number,
  currency: string,
  decimals: number
): string;

declare var moment: Moment;
