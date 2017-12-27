// Copyright (c) 2017, Libermatic and contributors
// For license information, please see license.txt

function set_loan_fields(
  frm,
  {
    name,
    loan_plan,
    rate_of_interest,
    calculation_slab,
    stipulated_recovery_amount,
    unset = false,
  }
) {
  frm.set_value('loan', unset ? null : name);
  frm.set_value('loan_plan', unset ? null : loan_plan);
  frm.set_df_property('loan_plan', 'read_only', unset ? 0 : 1);
  frm.set_value('calculation_slab', unset ? null : calculation_slab);
  frm.set_df_property('calculation_slab', 'read_only', unset ? 0 : 1);
  frm.set_value('rate_of_interest', unset ? null : rate_of_interest);
  frm.set_df_property('rate_of_interest', 'read_only', unset ? 0 : 1);
  frm.set_value(
    'stipulated_recovery_amount',
    unset ? null : stipulated_recovery_amount
  );
}

frappe.ui.form.on('Loan Application', {
  refresh: function(frm) {
    if (!frm.doc.__islocal) {
      if (frm.doc['status'] === 'Open') {
        frm.add_custom_button(__('Reject'), async function() {
          await frappe.call({
            method:
              'microfinance.microfinance_loan.doctype.loan_application.loan_application.reject',
            args: { name: frm.doc['name'] },
          });
          frm.reload_doc();
        });
        frm
          .add_custom_button(__('Approve'), async function() {
            const { message: loan } = await frappe.call({
              method:
                'microfinance.microfinance_loan.doctype.loan_application.loan_application.approve',
              args: { name: frm.doc['name'] },
            });
            frm.reload_doc();
            frappe.set_route('Form', 'Loan', loan);
          })
          .addClass('btn-primary');
      }
    }
    if (frm.doc['docstatus'] > 0) {
      frm.set_df_property('add_to_existing', 'hidden', 1);
    }
  },
  add_to_existing: async function(frm) {
    const { message } = await frappe.call({
      method: 'frappe.client.get_list',
      args: {
        doctype: 'Loan',
        fields: [
          'name',
          'posting_date',
          'disbursement_status',
          'recovery_status',
          'loan_plan',
          'loan_principal',
          'rate_of_interest',
          'calculation_slab',
          'stipulated_recovery_amount',
        ],
        filters: {
          customer: frm.doc['customer'],
          docstatus: 1,
        },
      },
    });
    if (message) {
      const dialog = new frappe.ui.Dialog({
        title: `Existing Loans for ${frm.doc['customer_name']}`,
        fields: [{ fieldname: 'ht', fieldtype: 'HTML' }],
      });
      const container = $('<table />').addClass(
        'table table-condensed table-striped'
      );
      container.append(
        $('<tr />')
          .append($('<th scope="col" />'))
          .append($('<th scope="col" />').text('Date'))
          .append($('<th scope="col" />').text('Loan'))
          .append($('<th scope="col" />').text('Status'))
          .append($('<th scope="col" class="text-right" />').text('Sanctioned'))
      );
      dialog.fields_dict.ht.$wrapper.append(container);
      dialog.set_primary_action(__('Select None'), function() {
        set_loan_fields(frm, { unset: true });
        dialog.hide();
      });
      message.forEach(
        ({
          name,
          posting_date,
          disbursement_status,
          recovery_status,
          loan_plan,
          loan_principal,
          rate_of_interest,
          calculation_slab,
          stipulated_recovery_amount,
        }) => {
          container.append(
            $('<tr />')
              .append(
                $('<td class="text-center" />').append(
                  $(
                    '<i class="octicon octicon-check" style="cursor: pointer;" />'
                  ).click(function() {
                    set_loan_fields(frm, {
                      name,
                      loan_plan,
                      rate_of_interest,
                      calculation_slab,
                      stipulated_recovery_amount,
                    });
                    dialog.hide();
                  })
                )
              )
              .append($('<td />').text(posting_date))
              .append(
                $('<td />').html(`<a href="#Form/Loan/${name}">${name}</a>`)
              )
              .append(
                $('<td />').text(`${disbursement_status} / ${recovery_status}`)
              )
              .append(
                $('<td class="text-right" />').text(
                  format_currency(
                    loan_principal,
                    frappe.defaults.get_default('currency'),
                    2
                  )
                )
              )
          );
        }
      );
      dialog.show();
    } else {
      frappe.msgprint(`${frm.doc['customer_name']} has no existing loans`);
    }
  },
  customer: function(frm) {
    set_loan_fields(frm, { unset: true });
  },
  loan_plan: async function(frm) {
    if (!frm.doc['loan']) {
      const { message = {} } = await frappe.db.get_value(
        'Loan Plan',
        frm.doc['loan_plan'],
        ['rate_of_interest', 'recovery_frequency', 'calculation_slab']
      );
      frm.set_value('rate_of_interest', message['rate_of_interest']);
      frm.set_value('recovery_frequency', message['recovery_frequency']);
      frm.set_value('calculation_slab', message['calculation_slab']);
    }
  },
});
