// Local FF:O instance only. Retired game endpoints become loopback requests.
const Java = bridge;
Java.perform(function () {
  const URL = Java.use('java.net.URL');
  const WebView = Java.use('android.webkit.WebView');
  function rateUrl(value) {
    const url=String(value);
    return /\/web\/statics\/probability\/sg_summons_list\.php(?:\?|$)/.test(url)
      ? 'http://127.0.0.1:11880/lapisProd/app/php/web/statics/probability/sg_summons_list.php'+(url.includes('?')?'?'+url.split('?')[1]:'') : url;
  }
  const post=WebView.postUrl.overload('java.lang.String','[B');
  post.implementation=function(url,data){return post.call(this,rateUrl(url),data);};
  const load=WebView.loadUrl.overload('java.lang.String');
  load.implementation=function(url){return load.call(this,rateUrl(url));};
  const init = URL.$init.overload('java.lang.String');
  init.implementation = function (value) {
    let url = String(value);
    if (/^https?:\/\/[^/]*(?:gumi\.sg|exvius\.com)(?:\/|$)/i.test(url)) {
      const path = url.replace(/^https?:\/\/[^/]+/i, '');
      send({event: 'route', path: path.split('?')[0]});
      url = 'http://127.0.0.1:11880' + path;
    }
    return init.call(this, url);
  };
  send({event: 'routing-ready'});
});
