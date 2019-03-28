# ECS781PMiniProject
A Flask python CrimeApp API was created for the purpose of the Cloud Computing course (ECS781P) - Queen Mary University of London.

API combines Metropolitan Police API together with the Google Geolocation API to obtain the crimes details in the specific areas. In order to functionate, it requires authentication.

## CrimeApp REST API REQUESTS


### Request

 * Check API
   GET /
   `http://127.0.0.1:5000/`
 
### Response
    
    Status: 200
    
    `Content-Type →application/json
     Content-Length →47
     Server →Werkzeug/0.15.1 Python/2.7.13
     Date →Thu, 28 Mar 2019 00:58:03 GMT` 
    
    `{"message": "welcome to the crimes api! "}`
   
### Request

 * Create User
   POST /
   `http://127.0.0.1:5000/createuser`
   
   `{"username":"your_username", "password":"your_password"}`
     
### Response

     Status: 201

    `Content-Type →application/json
     Content-Length →64
     Server →Werkzeug/0.15.1 Python/2.7.13
     Date →Thu, 28 Mar 2019 00:54:12 GMT`
   
    `{"message": "user username has been successfully created!"}`
     
### Request

 * Login
   POST /
   `http://127.0.0.1:5000/login`
     
   `{"username":"your_username", "password":"your_password"}`
     
### Response
     
     Status: 200
    
    `Content-Type →application/json
     Content-Length →305
     Server →Werkzeug/0.15.1 Python/2.7.13
     Date →Thu, 28 Mar 2019 01:05:58 GMT`
     
    `{"access_token":            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIxMjllY2YwMC05MTNiLTQ2ODEtYWY3MS01YzI1Nzk1MzhhMDIiLCJleHAiOjE1NTM3MzU3NTgsImZyZXNoIjpmYWxzZS  wiaWF0IjoxNTUzNzM1MTU4LCJ0eXBlIjoiYWNjZXNzIiwibmJmIjoxNTUzNzM1MTU4LCJpZGVudGl0eSI6InVzZXJuYW1lIn0.6ZdspeR1LqR_kFtkohySbHyu5Eo300lyWccn6ho1Pq   s"}`

### Request

 * Update Password
   PUT /
   Requires Bearer Token provided during the login
   `http://127.0.0.1:5000/updatepassword`
   
   `{"username":"your_username", "password":"new_password"}`
     
### Response

    Status: 200

    `Content-Type →application/json
     Content-Length →58
     Server →Werkzeug/0.15.1 Python/2.7.13
     Date →Thu, 28 Mar 2019 01:11:51 GMT`
   
    `{"message": "password has been successfully updated"}`

### Request

 * Delete user
   DELETE /
   Requires Bearer Token provided during the login
   `http://127.0.0.1:5000/deleteuser`
   
   `{"username":"your_username"}`
     
### Response

    Status: 200

   `Content-Type →application/json  
    Content-Length →54
    Server →Werkzeug/0.15.1 Python/2.7.13
    Date →Thu, 28 Mar 2019 01:14:22 GMT`
   
   `{"message": "user has been successfully deleted"}`
 
### Request

 * Get crimes details
   GET /
   Requires Bearer Token provided during the login
   `http://127.0.0.1:5000/records/your_postcode`
     
### Response

    Status: 200

   `Content-Type →text/html; charset=utf-8
    Content-Length →1406
    Server →Werkzeug/0.15.1 Python/2.7.13
    Date →Thu, 28 Mar 2019 01:22:23 GMT`
   
   `<!doctype html>
    <html>
      <head>
       <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.min.js"></script>
       <script src="https://code.jquery.com/jquery-2.1.4.min.js"></script>
       <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
      </head>
      <body> 
         <div id="graph-0"></div>  
         <div id="graph-1"></div>
         <script type="text/javascript">
var mygraphs = [{"data": [{"hole": 0.4, "labels": ["theft-from-the-person", "bicycle-theft", "anti-social-behaviour", "vehicle-crime", "possession-of-weapons", "shoplifting", "drugs", "criminal-damage-arson", "burglary", "robbery", "other-theft", "public-order", "other-crime", "violent-crime"], "name": "Category", "type": "pie", "values": [5, 10, 62, 56, 2, 1, 7, 16, 57, 17, 28, 24, 3, 97]}], "layout": {"title": "Crime Categoty Stats During 2019-01"}}, {"data": [{"hole": 0.4, "labels": ["Awaiting court outcome", "None", "Offender given a caution", "Local resolution", "Under investigation", "Investigation complete; no suspect identified"], "name": "Outcome", "type": "pie", "values": [10, 62, 1, 4, 235, 73]}], "layout": {"title": "Crime Outcome Stats During 2019-01"}}];
var ids = ['graph-0', 'graph-1'];

for(var i in mygraphs) {

Plotly.plot(ids[i], // the ID of the div, created above
            mygraphs[i].data,
            mygraphs[i].layout || {});
            console.log(mygraphs[i])
}
</script>
</body>
</html>`
