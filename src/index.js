import BillingPeriodDialog from './components/BillingPeriodDialog';
import LoaneeDetails from './components/LoaneeDetails';
import CalculatePrincipal from './components/CalculatePrincipal';
import LateChargesTool from './components/LateChargesTool';
import LoadingHandler from './utils/LoadingHandler';

// Enable LiveReload
if (__ENV__ !== 'production') {
  const script = document.createElement('script');
  script.src = `http://${
    (location.host || 'localhost').split(':')[0]
  }:35729/livereload.js?snipver=1`;
  document.body.appendChild(script);
}

export {
  LoadingHandler,
  BillingPeriodDialog,
  LoaneeDetails,
  CalculatePrincipal,
  LateChargesTool,
};
