// Build 9101's CRI downloader bypasses java.net.URL. Route only recovered
// FFBE asset requests and explicit loopback URLs; leave other traffic alone.
function installNativeAssetRoute(game) {
const start = game.getExportByName('_ZN20sgWrapCriFsInstaller5startEiRKNSt6__ndk112basic_stringIcNS0_11char_traitsIcEENS0_9allocatorIcEEEES8_S8_m');
function readString(object) {
  return (object.readU8() & 1) ? object.add(16).readPointer().readUtf8String()
    : object.add(1).readUtf8String(object.readU8() >> 1);
}
// Home's image loader consults only mounted CPKs. The one generated local
// navigation image lives on disk; load that exact file through Cocos instead.
const worldImage='/data/data/com.square_enix.android_googleplay.FFBEWW/files/en/sd/static_banner/home/ffo_world.png';
const textureCache=new NativeFunction(game.getExportByName('_ZN7cocos2d12TextureCache11getInstanceEv'),'pointer',[]);
const addImage=new NativeFunction(game.getExportByName('_ZN7cocos2d12TextureCache8addImageERKNSt6__ndk112basic_stringIcNS1_11char_traitsIcEENS1_9allocatorIcEEEE'),'pointer',['pointer','pointer']);
// FileManager::loadTexture, verified ARM64 Global 9.1.0 address.
Interceptor.attach(game.base.add(0x1f3b208),{
  onEnter(args){this.worldPath=readString(args[1])===worldImage?args[1]:null;},
  onLeave(result){
    if(!this.worldPath)return;
    const texture=addImage(textureCache(),this.worldPath);
    if(!texture.isNull()){result.replace(texture);send({event:'world-image-loaded'});}
  }
});
function localUrl(value) {
  let cleaned = value.replace(/^https?:\/\/(?=https?:\/\/127\.0\.0\.1:11880\/)/i, '');
  if (/^https?:\/\/127\.0\.0\.1:11880\//i.test(cleaned)) {
    return cleaned.replace(/^https:/i, 'http:').replace(/(\/dlc_assets_prod)\/+/,'$1/');
  }
  if (/^https?:\/\/[^/]*(?:gumi\.sg|exvius\.com)\//i.test(cleaned)) {
    return cleaned.replace(/^https?:\/\/[^/]+/i, 'http://127.0.0.1:11880');
  }
  return value;
}
Interceptor.attach(start, {
  onEnter(args) {
    const before = readString(args[2]);
    const after = localUrl(before);
    if (before === after) return;
    // start copies its const string argument immediately. Keep both temporary
    // buffers alive until that call returns; native code owns its own copy.
    this.bytes = Memory.allocUtf8String(after);
    this.object = Memory.alloc(24);
    this.object.writeU64((after.length + 16) | 1);
    this.object.add(8).writeU64(after.length);
    this.object.add(16).writePointer(this.bytes);
    args[2] = this.object;
    send({event:'native-asset-route',path:after.replace(/^http:\/\/127\.0\.0\.1:11880/,'').split('?')[0]});
  }
});
send({event:'native-asset-routing-ready'});
}
const readyTimer = setInterval(() => {
  const game = Process.findModuleByName('libgame.so');
  if (!game) return;
  clearInterval(readyTimer);
  installNativeAssetRoute(game);
}, 500);
