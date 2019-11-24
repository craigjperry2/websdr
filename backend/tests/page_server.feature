Feature: Serve a single page application and its assets via HTTP

  Scenario Outline: Serve page and assets
    
    Given the webserver is ready
     When a client connects with a web browser to <url> using <method>
     Then they receive an http response containing <content> with <code>

    Examples:
      | url                | method | code | content | description        |
      | /                  | GET    | 200  | </html> | A full html page   |
      | /missing           | GET    | 404  | </html> | An html error page |
      | /static/styles.css | GET    | 200  | h1 {    | A CSS stylesheet   |
