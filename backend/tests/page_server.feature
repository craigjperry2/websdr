Feature: Serve a single page application and its assets via HTTP

  Scenario Outline: Serve page and assets
    
    Given a client connects with a web browser to <url> using <method>
    When the webserver is ready
    Then they receive an http response containing <content> with <code>

    Examples:
      | url                | method | code | content                |
      | /                  | GET    | 200  | </html>                |
      | /missing           | GET    | 404  | {"detail":"Not Found"} |
      | /static/styles.css | GET    | 200  | h1 {                   |
