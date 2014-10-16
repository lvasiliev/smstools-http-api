smstools-http-api
=================

REST HTTP API with Flask for SMS Server Tools 3 (http://smstools3.kekekasvi.com/)


Installation
------------

After cloning, create a virtual environment and install the requirements. For Linux and Mac users:

    $ virtualenv venv
    $ source venv/bin/activate
    (venv) $ pip install -r requirements.txt

If you are on Windows, then use the following commands instead:

    $ virtualenv venv
    $ venv\Scripts\activate
    (venv) $ pip install -r requirements.txt

Running
-------

To run the server use the following command:

    (venv) $ python manage.py runserver --host 127.0.0.1 -r
     * Running on http://127.0.0.1:5000/
     * Restarting with reloader

Then from a different terminal window you can send requests.

API Documentation
-----------------

- POST **/api/v1.0/sms/outgoing**

    Sending new sms message.<br>
    The body must contain a JSON object that defines `mobiles` array and `text` fields.<br>
    On success a status code 201 is returned. The body of the response contains a JSON object:
    - `message_id` - object contains phone numbers and their files (message_id) in spool directory.
    - `parts_count` - how many parts the sms will be sent.
    - `sent_text` - text of a SMS message.

    On failure status code 400 (bad request) is returned.<br>
    If enabled MOBILE_PERMS option in config.py you may restrict phone numbers for users.<br> 


- GET **/api/v1.0/sms/sent/&lt;path:message_id&gt;**

    Getting information of the sent message using message_id.<br>
    The body of the response contains a JSON object with the requested message_id:
    - `From` - user who sent.
    - `To` - phone number of the recipient.
    - `Sent` - time of sent sms message.
    - `message_id` - files (message_id) in spool directory.

    On failure status code 404 (not found) is returned.<br>
    
    Notes:
    - In a production deployment secure HTTP must be used to protect the password in transit.

Example
-------

The following `curl` command sending sms:

    % curl -u lvv:SecretPAss -i -H "Content-Type: application/json; charset=UTF-8" -X POST -d '{"text":"Hi, Jack!", "mobiles":["79680000000", "79160000000"]}' http://127.0.0.1:5000/api/v1.0/sms/outgoing
    HTTP/1.0 201 CREATED
    Content-Type: application/json
    Content-Length: 154
    Server: Werkzeug/0.9.6 Python/2.7.8
    Date: Tue, 13 Oct 2014 11:36:57 GMT

    {
        "message_id": {
            "79160000000": "smsgw.http.2bpDiR",
            "79680000000": "smsgw.http.ML5dOj"
        },
    "parts_count": 1,
    "sent_text": "Hi, Jack!"
    } 

The following `curl` command getting information of the sent message:

    % curl -u lvv:SecretPAss -i -H "Content-Type: application/json; charset=UTF-8" http://127.0.0.1:5000/api/v1.0/sms/sent/smsgw.http.2bpDiR
    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 94
    Server: Werkzeug/0.9.6 Python/2.7.8
    Date: Tue, 13 Oct 2014 11:46:45 GMT

    {
        "From": "lvv",
        "Sent": "14-10-13 11:37:09",
        "To": "79160000000",
        "message_id": "smsgw.http.2bpDiR"
    } 

Using the wrong message_id:

    % curl -u lvv:SecretPAss -i -H "Content-Type: application/json; charset=UTF-8" http://127.0.0.1:5000/api/v1.0/sms/sent/smsgw.http.TqvEdt
    HTTP/1.0 404 NOT FOUND
    Content-Type: application/json
    Content-Length: 26
    Server: Werkzeug/0.9.6 Python/2.7.8
    Date: Tue, 13 Oct 2014 10:16:42 GMT

    {
        "error": "Not found"
    }


**v0.1** - Initial release.
