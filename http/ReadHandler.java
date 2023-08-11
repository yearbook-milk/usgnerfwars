
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


public class ReadHandler implements HttpHandler {
    public void handle(HttpExchange t) throws IOException {
      System.out.println("---- New request! ----");

		File f;

      try {
		// send this because the HTML client that presents a GUI to read this stuff isnt
		// on the same host as this http server
		t.getResponseHeaders().set("Access-Control-Allow-Origin", "*");  
		  
		// print dbg info
        System.out.println(t.getRequestMethod() + " " + t.getRequestURI());
        System.out.println(t.getRequestHeaders());

		// parse URL
        String[] components = t.getRequestURI().toString().split("/");
        String[] acceptable = {"detectorfilterdata.txt", "detectorpipeline.txt", "tracker.txt", "doc.txt", ",config.py"};
        boolean pass = false;
		
		// check that the file can be read from
        for (String filename : acceptable) {
          if (filename.equals(components[2])) {
            pass = true; 
          }
        }
        if (pass == false) {
          Helper.reply_over_HTTP(t, 403, "403: Access denied");
        } else {
		  // if the user is allowed to read from the requested file...
          // open it 
		  if (components[2].substring(0,1).equals(",")) {
			f = new File("../" + components[2].substring(1));
		  } else {
			f = new File("../computervision/" + components[2]);
		  }
		  // read it
          Scanner fr = new Scanner(f);
          String output = "";
          while (fr.hasNextLine()) {
            output += fr.nextLine();
			output += "\n";
          }
          fr.close();
		  // put it in the HTTP response body and send it
          Helper.reply_over_HTTP(t, 200, output);
        }
      } catch (Exception e) {
        System.out.println("500 Internal Server Error: " + e.getStackTrace().toString());
        Helper.reply_over_HTTP(t, 500, "500: Internal Server Error" + e.getStackTrace().toString());
      }
    }
  }