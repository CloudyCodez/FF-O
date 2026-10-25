package com.cloud.ffo;
import android.content.Context;import org.json.*;import java.io.*;import java.net.*;import java.security.*;import java.util.zip.*;
final class DataSetup {
 interface Progress {void update(String value);}
 private static InputStream fetch(String address)throws IOException{
  URL url=new URL(address);if(!"https".equals(url.getProtocol()))throw new IOException("Expected secure download URL");
  HttpURLConnection c=(HttpURLConnection)url.openConnection();c.setConnectTimeout(20000);c.setReadTimeout(60000);c.setRequestProperty("User-Agent","FFO-Hub");if(c.getResponseCode()!=200){int code=c.getResponseCode();c.disconnect();throw new IOException("Download HTTP "+code+". Try again later.");}return new FilterInputStream(c.getInputStream()){public void close()throws IOException{try{super.close();}finally{c.disconnect();}}};
 }
 static void install(Context context,Progress progress)throws Exception{
  File root=new File(context.getExternalFilesDir(null),"runtime");root.mkdirs();File marker=new File(root,"data-manifest.json");
  progress.update("Reading tester data manifest…");JSONObject metadata;
  try(InputStream in=fetch("https://github.com/CloudyCodez/FF-O/releases/download/v0.1.0/FFO-Download.json")){ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1){out.write(b,0,n);if(out.size()>4000000)throw new IOException("Manifest too large");}metadata=new JSONObject(out.toString("UTF-8"));}
  if(metadata.getInt("schema")!=1)throw new IOException("Unsupported data manifest");
  if(marker.exists()&&!marker.delete())throw new IOException("Cannot reset data completion marker");
  File cache=new File(root,"assets/cache");cache.mkdirs();String prefix=cache.getCanonicalPath()+File.separator;
  try(Parts stream=new Parts(metadata.getJSONArray("parts"),progress);ZipInputStream zip=new ZipInputStream(new BufferedInputStream(stream,65536))){ZipEntry entry;byte[] buffer=new byte[65536];while((entry=zip.getNextEntry())!=null){File file=new File(cache,entry.getName());if(!file.getCanonicalPath().startsWith(prefix))throw new IOException("Unsafe data archive path");if(entry.isDirectory()){file.mkdirs();continue;}file.getParentFile().mkdirs();File temp=new File(file.getPath()+".download");try(OutputStream out=new FileOutputStream(temp)){int n;while((n=zip.read(buffer))!=-1)out.write(buffer,0,n);}if(file.exists()&&!file.delete())throw new IOException("Cannot replace "+file.getName());if(!temp.renameTo(file))throw new IOException("Cannot install "+file.getName());}stream.finish();}
  JSONArray files=metadata.getJSONArray("files");for(int i=0;i<files.length();i++){JSONObject row=files.getJSONObject(i);File file=new File(cache,row.getString("path"));if(!file.getCanonicalPath().startsWith(prefix)||!file.isFile()||file.length()!=row.getLong("bytes"))throw new IOException("Incomplete game data: "+row.getString("path"));}
  JSONObject complete=new JSONObject().put("files",files).put("bytes",metadata.getLong("bytes"));File staged=new File(root,"data-manifest.tmp");try(FileOutputStream out=new FileOutputStream(staged)){out.write(complete.toString().getBytes("UTF-8"));out.getFD().sync();}if(!staged.renameTo(marker))throw new IOException("Cannot finish data setup");
 }
 private static final class Parts extends InputStream {
  final JSONArray parts;final Progress progress;int index=-1;InputStream current;MessageDigest digest;long count;JSONObject item;long last;
  Parts(JSONArray parts,Progress p){this.parts=parts;progress=p;}
  private boolean advance()throws IOException{
   if(current!=null){current.close();current=null;StringBuilder hash=new StringBuilder();for(byte b:digest.digest())hash.append(String.format("%02x",b&255));try{if(count!=item.getLong("bytes")||!hash.toString().equals(item.getString("sha256")))throw new IOException("Data part verification failed; retry download.");}catch(JSONException e){throw new IOException(e);}}
   if(++index>=parts.length())return false;
   try{item=parts.getJSONObject(index);current=fetch(item.getString("url"));digest=MessageDigest.getInstance("SHA-256");count=0;progress.update("Downloading data part "+(index+1)+" of "+parts.length());return true;}catch(Exception e){throw new IOException(e);}
  }
  public int read()throws IOException{byte[] b=new byte[1];int n=read(b,0,1);return n<0?-1:b[0]&255;}
  public int read(byte[] b,int off,int len)throws IOException{if(len==0)return 0;if(current==null&&!advance())return -1;int n=current.read(b,off,len);if(n<0){if(!advance())return -1;return read(b,off,len);}digest.update(b,off,n);count+=n;long now=System.currentTimeMillis();if(now-last>1500){progress.update("Downloading part "+(index+1)+" / "+parts.length()+" · "+(count/1048576)+" MB");last=now;}return n;}
  void finish()throws IOException{byte[] b=new byte[65536];while(read(b)!=-1){}}
  public void close()throws IOException{if(current!=null){current.close();current=null;}}
 }
}
