import type Moment from './npm/moment_v2.x.x';

declare class FieldGroup {
  constructor({ fields: Array<any>, parent: ?HTMLElement }): void;
  fields_list: Array<any>;
  set_value(key: string, value: mixed): void;
  get_value(kye: string): mixed;
  make(): void;
}

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
  ui: { FieldGroup: typeof FieldGroup }
}

declare function format_currency(
  v: number,
  currency: string,
  decimals: number
): string;

declare var moment: Moment;
