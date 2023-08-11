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

public class Main {

  // thank you to
  // https://stackoverflow.com/questions/3732109/simple-http-server-in-java-using-only-java-se-api
  // for the HTTP server code
  public static void main(String[] args) throws Exception {
	
	  // start the server on the port in the .PORT file in this dir
	  File f = new File(".PORT");
	  Scanner fr = new Scanner(f);
	  String output = "";
	  while (fr.hasNextLine()) {
		output += fr.nextLine();
	  }
	  fr.close();
	  int port_number = Integer.parseInt(output.toString());
		  
		  
    HttpServer server = HttpServer.create(new InetSocketAddress(port_number), 0);
    server.createContext("/read", new ReadHandler());
    server.createContext("/push", new WriteHandler());
    server.setExecutor(null); // creates a default executor
    server.start();
    System.out.println("CAS Config Update Service: HTTP server started on port# "+port_number);
  }



  

}