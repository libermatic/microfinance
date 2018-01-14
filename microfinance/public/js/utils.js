frappe.provide('microfinance');
frappe.provide('microfinance.utils');

microfinance.utils.check_billing_vs_due_date = function(billing_day, due_day) {
  return (
    moment(due_day).isAfter(billing_day) &&
    moment(due_day).diff(billing_day, 'days') < 31
  );
};

class BillingPeriodDialog extends frappe.ui.Dialog {
  constructor(props) {
    super({
      title: 'Billing Periods',
      fields: [
        { fieldname: 'actions', fieldtype: 'HTML' },
        { fieldname: 'ht', fieldtype: 'HTML' },
      ],
    });
    this.props = props;
    this.state = {
      loan: props.frm.doc['loan'],
      date: frappe.datetime.nowdate(),
    };
    this.render_content();
  }
  async update_state(state) {
    const prev_state = this.state;
    this.state = Object.assign({}, this.state, state);
    this.render_content(prev_state);
  }
  render_content(prev_state = {}) {
    if (this.state.date !== prev_state.date) {
      this.render_actions().then(node => {
        this.fields_dict['actions'].$wrapper.empty();
        this.fields_dict['actions'].$wrapper.append(node);
        this.fetch_data();
      });
    }
    if (
      this.state.periods !== prev_state.periods ||
      this.state.loading !== prev_state.loading
    ) {
      this.render_table().then(node => {
        this.fields_dict['ht'].$wrapper.empty();
        this.fields_dict['ht'].$wrapper.append(node);
      });
    }
  }
  async render_actions() {
    const container = $('<div />').addClass('microf-dialog-actions');
    const prev = $(
      '<button class="btn btn-info"><i class="octicon octicon-chevron-left"/> Previous</button>'
    ).click(() => {
      this.update_state({
        date: frappe.datetime.add_months(this.state.date, -5),
      });
    });
    const current = $('<button class="btn btn-info">Current</button>').click(
      () => {
        this.update_state({ date: frappe.datetime.nowdate() });
      }
    );
    const next = $(
      '<button class="btn btn-info">Next <i class="octicon octicon-chevron-right"/></button>'
    ).click(() => {
      this.update_state({
        date: frappe.datetime.add_months(this.state.date, 5),
      });
    });
    const none = $('<button class="btn btn-danger">None</button>');
    container
      .append(
        $('<div class="btn-group" />')
          .append(prev)
          .append(current)
          .append(next)
      )
      .append(none);
    return container;
  }
  async fetch_data() {
    try {
      const { loan, date } = this.state;
      this.update_state({ loading: true });
      const { message: periods } = await frappe.call({
        method:
          'microfinance.microfinance_loan.doctype.loan.loan.get_billing_periods',
        args: { loan, interval_date: date },
      });
      this.update_state({ periods });
    } catch (e) {
      frappe.throw(e.toString());
    } finally {
      this.update_state({ loading: false });
    }
  }
  async render_table() {
    const { loading, periods } = this.state;
    if (loading) {
      const loading_indicator = $('<div />')
        .addClass('microf-dialog-loading')
        .text('Loading');
      return loading_indicator;
    }
    const container = $('<table />').addClass(
      'table table-condensed table-striped table-hover'
    );
    container.append(
      $('<tr />')
        .append($('<th scope="col" />').text('Period'))
        .append($('<th scope="col" class="text-right" />').text('Interest'))
    );
    if (periods) {
      periods.forEach(({ start_date, end_date, interest }) => {
        container.append(
          $('<tr style="cursor: pointer;" />')
            .append(
              $('<td />').text(
                `${frappe.datetime.str_to_user(
                  start_date
                )} - ${frappe.datetime.str_to_user(end_date)} (${moment(
                  start_date
                ).format('MMM, YYYY')})`
              )
            )
            .append(
              $('<td class="text-right" />').text(
                format_currency(
                  interest,
                  frappe.defaults.get_default('currency'),
                  2
                )
              )
            )
            .click(() => {
              this.props.on_select({
                period: `${start_date} - ${end_date}`,
                interest,
              });
              this.hide();
            })
        );
      });
    }
    return container;
  }
}

microfinance.utils.BillingPeriodDialog = BillingPeriodDialog;
