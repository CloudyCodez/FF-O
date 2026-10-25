package com.cloud.ffo;
import java.nio.charset.StandardCharsets;import java.security.MessageDigest;
final class AccessGate {
 static volatile boolean unlocked=false;
 static boolean check(String value){try{byte[] actual=MessageDigest.getInstance("SHA-256").digest(value.getBytes(StandardCharsets.UTF_8));byte[] expected=new byte[32];String hash="a911e2cdb9279cf48c17aaf38190edfaace0c6bdfc52a5822dfb4cef4ae916a2";for(int i=0;i<32;i++)expected[i]=(byte)Integer.parseInt(hash.substring(i*2,i*2+2),16);return MessageDigest.isEqual(actual,expected);}catch(Exception e){return false;}}
}
