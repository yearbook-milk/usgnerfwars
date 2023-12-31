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


public class Helper {
  public static void reply_over_HTTP(HttpExchange t, int code, String responseText) throws IOException {
	// set the HTTP success/error code
    t.sendResponseHeaders(code, responseText.length());
	
	// write to the stream representing the response output, and close it, which ends the response actions and thus the current exchange
    OutputStream os = t.getResponseBody();
    os.write(responseText.getBytes());
    os.close();
    t.close();
  }
}