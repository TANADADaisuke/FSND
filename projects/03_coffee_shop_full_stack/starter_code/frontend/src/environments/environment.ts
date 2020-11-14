/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'noradai.us.auth0.com', // the auth0 domain prefix
    audience: 'cafe', // the audience set for the auth0 app
    clientId: 't7RGJnCXEnNpnT089mCPx6XKPrSmqGmR', // the client id generated for the auth0 app
    callbackURL: 'https://localhost:8100', // the base url of the running ionic application. 
  }
};
