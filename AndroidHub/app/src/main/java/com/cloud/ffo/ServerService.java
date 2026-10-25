package com.cloud.ffo;
import android.app.*;import android.content.*;import android.os.*;import android.util.Log;
import com.chaquo.python.*;import com.chaquo.python.android.AndroidPlatform;
import java.io.*;import java.util.zip.*;
public class ServerService extends Service {
 public static volatile String status="Stopped";
 private PyObject runtime;private PowerManager.WakeLock wake;private boolean starting;
 public void onCreate(){super.onCreate();NotificationManager nm=getSystemService(NotificationManager.class);nm.createNotificationChannel(new NotificationChannel("server","FF:O local server",NotificationManager.IMPORTANCE_LOW));PendingIntent pi=PendingIntent.getActivity(this,0,new Intent(this,MainActivity.class),PendingIntent.FLAG_IMMUTABLE);startForeground(1,new Notification.Builder(this,"server").setContentTitle("FF:O local server").setContentText("Running on this phone").setSmallIcon(android.R.drawable.stat_notify_sync).setContentIntent(pi).build());}
 public int onStartCommand(Intent i,int flags,int id){if(!AccessGate.unlocked){report("Unlock Hub before starting the server.");stopSelf();return START_NOT_STICKY;}if(starting)return START_NOT_STICKY;starting=true;report("Preparing server…");
 new Thread(()->{try{
 wake=((PowerManager)getSystemService(POWER_SERVICE)).newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"FFO:Server");wake.acquire();
 if(i!=null&&"download".equals(i.getAction())){DataSetup.install(this,value->report(value));report("Game data ready. You can start the server.");starting=false;stopSelf();return;}
 File root=new File(getFilesDir(),"runtime");root.mkdirs();
 try(ZipInputStream zin=new ZipInputStream(getAssets().open("runtime.zip"))){ZipEntry entry;byte[] b=new byte[65536];while((entry=zin.getNextEntry())!=null){File out=new File(root,entry.getName());if(!out.getCanonicalPath().startsWith(root.getCanonicalPath()+File.separator))throw new IOException("Invalid runtime path");if(entry.isDirectory()){out.mkdirs();continue;}out.getParentFile().mkdirs();try(OutputStream stream=new FileOutputStream(out)){int n;while((n=zin.read(b))!=-1)stream.write(b,0,n);}}}
 synchronized(ServerService.class){if(!Python.isStarted())Python.start(new AndroidPlatform(this));}
 runtime=Python.getInstance().getModule("phone_runtime");report(runtime.callAttr("start",root.getAbsolutePath(),new File(getExternalFilesDir(null),"runtime").getAbsolutePath()).toString());
 
 }catch(Exception e){report("Server error: "+Log.getStackTraceString(e));Log.e("FFOHub",status,e);starting=false;stopSelf();}},"FFOStartup").start();return START_NOT_STICKY;}
 private void report(String value){status=value;try(FileOutputStream out=new FileOutputStream(new File(getFilesDir(),"server-status.txt"))){out.write(value.getBytes(java.nio.charset.StandardCharsets.UTF_8));}catch(IOException ignored){}}
 public IBinder onBind(Intent i){return null;}
 public void onDestroy(){PyObject old=runtime;runtime=null;new Thread(()->{try{if(old!=null)old.callAttr("stop");}catch(Exception e){Log.e("FFOHub","Stop",e);}finally{if(wake!=null&&wake.isHeld())wake.release();if(!status.startsWith("Server error")&&!status.startsWith("Game data ready"))report("Stopped");}}).start();super.onDestroy();}
}
