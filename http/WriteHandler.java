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
	  
	  FileWriter f;

      try {
		  // this header needs to be set because the HTML client that presents a GUI to edit this stuff
		  // is not run on the same host as this server
		  t.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
		  
		// print debug info 
        System.out.println(t.getRequestMethod() + " " + t.getRequestURI());
        System.out.println(t.getRequestHeaders());
		
        // get post body
        BufferedReader post_body_stream = new BufferedReader(new InputStreamReader(t.getRequestBody()));
        String inputLine;
        StringBuffer post_body = new StringBuffer();

        while ((inputLine = post_body_stream.readLine()) != null) {
          post_body.append(inputLine);
        }
        post_body_stream.close();
		
		System.out.println("Req. body: "+post_body.toString());

        // parse URL
        String[] components = t.getRequestURI().toString().split("/");
        String[] acceptable = {"detectorfilterdata.txt", "detectorpipeline.txt", "tracker.txt", ",config.py"};
        boolean pass = false;
		
		// check if the user is trying to write to a file that they shouldn't be able to
        for (String filename : acceptable) {
          if (filename.equals(components[2])) {
            pass = true;
          }
        }
        if (pass == false) {
          Helper.reply_over_HTTP(t, 403, "403: Write access denied");
        } else {
		  // if the user is authorized to write to this file...
          // open the file up and write to it
		  if (components[2].substring(0,1).equals(",")) {
			f = new FileWriter("../" + components[2].substring(1));
		  } else {
			f = new FileWriter("../computervision/" + components[2]);
		  }
          f.write(post_body.toString());
          f.close();
		  
		  // send a response
          Helper.reply_over_HTTP(t, 200, post_body.toString());
        }
      } catch (Exception e) {
        System.out.println("500 Internal Server Error: " + e.getStackTrace().toString());
        Helper.reply_over_HTTP(t, 500, "500: Internal Server Error" + e.getStackTrace().toString());
      }
    }
  }