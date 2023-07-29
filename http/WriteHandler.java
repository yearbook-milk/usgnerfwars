import java.io.*;
import java.io.IOException;

import java.util.Iterator;
import java.util.Scanner;

import java.net.*;
import java.net.InetSocketAddress;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import org.json.simple.*;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;


public class WriteHandler implements HttpHandler {
    public void handle(HttpExchange t) throws IOException {
      System.out.println("---- New request! ----");

      try {
		  
		  t.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
		  
		  
        System.out.println(t.getRequestMethod() + " " + t.getRequestURI());
        System.out.println(t.getRequestHeaders());
        // We need the post body here
        BufferedReader post_body_stream = new BufferedReader(new InputStreamReader(t.getRequestBody()));
        String inputLine;
        StringBuffer post_body = new StringBuffer();

        while ((inputLine = post_body_stream.readLine()) != null) {
          post_body.append(inputLine);
        }
        post_body_stream.close();
		
		System.out.println("Req. body: "+post_body.toString());

        String[] components = t.getRequestURI().toString().split("/");
        String[] acceptable = {"detectorfilterdata.txt", "detectorpipeline.txt", "tracker.txt"};
        boolean pass = false;
        for (String filename : acceptable) {
          if (filename.equals(components[2])) {
            pass = true;
          }
        }
        if (pass == false) {
          Helper.reply_over_HTTP(t, 403, "403: Write access denied");
        } else {
          // Send the reply using roHTTP
          FileWriter f = new FileWriter("../computervision/" + components[2]);
          f.write(post_body.toString());
          f.close();
          Helper.reply_over_HTTP(t, 200, post_body.toString());
        }
      } catch (Exception e) {
        System.out.println("500 Internal Server Error: " + e.getStackTrace().toString());
        Helper.reply_over_HTTP(t, 500, "500: Internal Server Error" + e.getStackTrace().toString());
      }
    }
  }