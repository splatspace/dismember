var querystring = require('querystring');
var restler = require('restler-q');

var config = require('../config/config');

/**
 * Gets a URL from WePay that you can send to the end-user so they can authorize your
 * account to access their account for the purpose you specify.
 *
 * When the user finally reaches your redirectUri, the query params include a 'code', which
 * you will need to save for calls to getAccessToken.  The query params also include 'state',
 * if you supplied any.
 *
 * @param {string} redirectUri the URI you want the user to come back to after completing the web authorization
 * @param {string|string[]} scope the WePay authorization scopes you want (see WePay API documentation for valid strings)
 * @param {string} [state] your state data; is carried through the auth flow and returns as a query param when the user reaches your redirectUri
 * @returns {string} the URL to send to the user so they can authorize your access to their account
 */
exports.getAuthorizeUrl = function (redirectUri, scope, state) {
  var baseUrl;
  if (config.wePayApi.environment === 'prod') {
    baseUrl = 'https://www.wepay.com/v2/oauth2/authorize';
  } else if (config.wePayApi.environment === 'stage') {
    baseUrl = 'https://stage.wepay.com/v2/oauth2/authorize';
  }

  if (!redirectUri) {
    throw 'redirectUri is required';
  }
  if (!scope) {
    throw 'scope is required';
  }

  var params = {
    client_id: config.wePayApi.clientId,
    redirect_uri: redirectUri,
    scope: scope
  }

  // These are optional
  if (state) {
    params.state = state;
  }

  return baseUrl + '?' + querystring.stringify(params);
}

/**
 * Gets an access token for making API requests.  You must first call getAuthorizeUrl to
 * obtain 'code'.
 *
 * @param {string} redirectUri the URI that you used for getAuthorizeUrl
 * @param {string} code the code you got back as a query param from getAuthorizeUrl
 * @param {string} [ipnUri] a URI to receive callbacks
 * @returns a promise that resolves to an access token string
 */
exports.getAccessToken = function (redirectUri, code, ipnUri) {
  var baseUrl;
  if (config.wePayApi.environment === 'prod') {
    baseUrl = 'https://wepayapi.com/v2/oauth2/token';
  } else if (config.wePayApi.environment === 'stage') {
    baseUrl = 'https://stage.wepayapi.com/v2/oauth2/token';
  }

  if (!redirectUri) {
    throw 'redirectUri is required and must match the URI used to authorize';
  }
  if (!code) {
    throw 'code is required';
  }

  var params = {
    client_id: config.wePayApi.clientId,
    redirect_uri: redirectUri,
    client_secret: config.wePayApi.clientSecret,
    code: code
  }

  // These are optional
  if (ipnUri) {
    params.callback_uri = ipnUri;
  }

  var url = baseUrl + '?' + querystring.stringify(params);
  return restler.get(url);
}

/**
 * Call a WePay service method.
 *
 * @param {string} accessToken an access token you obtained from getAccessToken()
 * @param {string} method the name of the method (like '/checkout/create')
 * @param {object} params the parameters to the call
 * @returns a promise that resolves to the method response data object
 */
exports.call = function (accessToken, method, params) {
  var baseUrl;
  if (config.wePayApi.environment === 'prod') {
    baseUrl = 'https://wepayapi.com/v2';
  } else if (config.wePayApi.environment === 'stage') {
    baseUrl = 'https://stage.wepayapi.com/v2';
  }

  if (!accessToken) {
    throw 'accessToken is required';
  }
  if (!method) {
    throw 'method is required';
  }

  var headers = {
    'Authorization': 'Bearer ' + accessToken
  };

  var url = baseUrl + method;
  return restler.post(url, { data: params, headers: headers });
}