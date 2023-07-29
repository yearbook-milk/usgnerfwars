
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

      try {
        System.out.println(t.getRequestMethod() + " " + t.getRequestURI());
        System.out.println(t.getRequestHeaders());
        // For this, we just process the URL and return the contents of the appropriate file,
        // assuming that this file is on the list that is allowed to be exposed.

        String[] components = t.getRequestURI().toString().split("/");
        String[] acceptable = {"detectionfilterdata.txt", "detectorpipeline.txt", "tracker.txt"};
        boolean pass = false;
        for (String filename : acceptable) {
          if (filename.equals(components[2])) {
            pass = true;
          }
        }
        if (pass == false) {
          Helper.reply_over_HTTP(t, 403, "403: Access denied");
        } else {
          // Send the reply using roHTTP
          File f = new File("../computervision/" + components[2]);
          Scanner fr = new Scanner(f);
          String output = "";
          while (fr.hasNextLine()) {
            output += fr.nextLine();
          }
          fr.close();
          Helper.reply_over_HTTP(t, 200, output);
        }
      } catch (Exception e) {
        System.out.println("500 Internal Server Error: " + e.getStackTrace().toString());
        Helper.reply_over_HTTP(t, 500, "500: Internal Server Error" + e.getStackTrace().toString());
      }
    }
  }