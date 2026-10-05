package com.michelslab.igcleaner;

import android.content.Context;
import android.content.SharedPreferences;
import org.json.*;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public final class SyncApi {
    private final SharedPreferences prefs;
    private String url, key, access, refresh, userEmail;
    public SyncApi(Context c){ prefs=c.getSharedPreferences("igc_sync",Context.MODE_PRIVATE); load(); }
    public void configure(String u,String k,String email){ url=trim(u); key=k.trim(); userEmail=email.trim(); prefs.edit().putString("url",url).putString("key",key).putString("email",userEmail).apply(); }
    public String getUrl(){return url;} public String getKey(){return key;} public String getEmail(){return userEmail;} public boolean hasSession(){return access!=null&&!access.isEmpty();}
    private String trim(String s){return s==null?"":s.trim().replaceAll("/+$","");}
    private void load(){url=prefs.getString("url","");key=prefs.getString("key","");userEmail=prefs.getString("email","");access=prefs.getString("access","");refresh=prefs.getString("refresh","");}
    private void saveSession(JSONObject j){access=j.optString("access_token","");refresh=j.optString("refresh_token",refresh);prefs.edit().putString("access",access).putString("refresh",refresh).apply();}
    public JSONObject login(String password) throws Exception { JSONObject b=new JSONObject().put("email",userEmail).put("password",password); JSONObject r=request("POST","/auth/v1/token?grant_type=password",b,false,null); saveSession(r); return r; }
    public JSONObject signup(String password) throws Exception { JSONObject b=new JSONObject().put("email",userEmail).put("password",password); JSONObject r=request("POST","/auth/v1/signup",b,false,null); if(r.has("access_token"))saveSession(r); return r; }
    public void logout(){access="";refresh="";prefs.edit().remove("access").remove("refresh").apply();}
    private boolean refresh() { try{ if(refresh==null||refresh.isEmpty())return false; JSONObject r=request("POST","/auth/v1/token?grant_type=refresh_token",new JSONObject().put("refresh_token",refresh),false,null); saveSession(r); return !access.isEmpty(); }catch(Exception e){return false;} }
    private JSONObject request(String method,String path,JSONObject body,boolean auth,Map<String,String> extra) throws Exception { String s=raw(method,path,body==null?null:body.toString(),auth,extra); return s.isEmpty()?new JSONObject():new JSONObject(s); }
    private String raw(String method,String path,String body,boolean auth,Map<String,String> extra) throws Exception {
        if(url.isEmpty()||key.isEmpty())throw new IllegalStateException("Falta URL/key de Supabase");
        HttpURLConnection c=(HttpURLConnection)new URL(url+path).openConnection();c.setRequestMethod(method);c.setConnectTimeout(15000);c.setReadTimeout(20000);c.setRequestProperty("apikey",key);c.setRequestProperty("Content-Type","application/json");if(auth&&!access.isEmpty())c.setRequestProperty("Authorization","Bearer "+access);if(extra!=null)for(Map.Entry<String,String> e:extra.entrySet())c.setRequestProperty(e.getKey(),e.getValue());if(body!=null){c.setDoOutput(true);try(OutputStream os=c.getOutputStream()){os.write(body.getBytes(StandardCharsets.UTF_8));}}
        int code=c.getResponseCode();InputStream is=code>=200&&code<300?c.getInputStream():c.getErrorStream();String txt="";if(is!=null){try(BufferedReader br=new BufferedReader(new InputStreamReader(is,StandardCharsets.UTF_8))){StringBuilder sb=new StringBuilder();String line;while((line=br.readLine())!=null)sb.append(line);txt=sb.toString();}}
        if((code==401||code==403)&&auth&&refresh()){return raw(method,path,body,true,extra);}if(code<200||code>=300)throw new IOException("HTTP "+code+" "+txt);return txt;
    }
    public JSONArray get(String tableQuery) throws Exception { String s=raw("GET","/rest/v1/"+tableQuery,null,true,null);return s.isEmpty()?new JSONArray():new JSONArray(s); }
    public void upsert(String table,String conflict,JSONArray rows) throws Exception { Map<String,String> h=new HashMap<>();h.put("Prefer","resolution=merge-duplicates,return=minimal");raw("POST","/rest/v1/"+table+"?on_conflict="+URLEncoder.encode(conflict,"UTF-8"),rows.toString(),true,h); }
    public void patch(String tableQuery,JSONObject body) throws Exception { Map<String,String> h=new HashMap<>();h.put("Prefer","return=minimal");raw("PATCH","/rest/v1/"+tableQuery,body.toString(),true,h); }
    public void insert(String table,JSONArray rows) throws Exception { Map<String,String> h=new HashMap<>();h.put("Prefer","resolution=merge-duplicates,return=minimal");raw("POST","/rest/v1/"+table,rows.toString(),true,h); }
}