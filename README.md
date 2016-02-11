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

If you decide to run this application under a different user than `smsd`, you need to adjust the `outgoing` spooler directory to retain proper permissions for newly created files or `smsd` won't be able to process the messages.

    # Debian, Ubuntu
    chmod g+s /var/spool/sms/outgoing
    setfacl -m d:g:smsd:rwX /var/spool/sms/outgoing

    # Fedora, RHEL
    chmod g+s /var/spool/sms/outgoing
    setfacl -m d:g:smstools:rwX /var/spool/sms/outgoing

You need to have file system ACLs enabled for this to work.


API Documentation
-----------------

- `POST /api/v1.0/sms/outgoing`

    Send a new SMS.

    The body must contain a JSON object that defines `mobiles` array and `text` fields. Status code 201 is returned on success. Body of the response contains following JSON object:

    - `message_id` - Mapping of supplied numbers to their corresponding spooler file names (ids).
    - `parts_count` - Tells you how many parts will the SMS be split into.
    - `sent_text` - Original message text.

    Status code 400 (Bad Request) is returned in case of a failure to parse input data.

    If `USER_WHITELIST` option is enabled in the `config.py`, number access control lists are applied.

- `GET /api/v1.0/sms/outgoing?text=Hi+Jack!&mobiles=79680000000,79160000000`

    Send a new SMS.

    The parameters must contain a `mobiles` (separate each entry with comma) and `text` fields. Status code 201 is returned on success. Body of the response contains following JSON object as describe above.


- `GET /api/v1.0/sms/<kind>/<string:message_id>`

    Get information about a message.

    Where `kind` can be one of `incoming`, `outgoing`, `checked`, `failed`, or `sent`. Body of the response contains a JSON object with all headers and following two fields:

    - `message_id` - Unique identifier of the message.
    - `text` - Text of the message.

    Status code 404 (Not Found) signifies that no message with such an `message_id` has been found.

- `GET /api/v1.0/sms/<kind>/`

    List messages of given `kind`.

    Where `kind` can be one of `incoming`, `outgoing`, `checked`, `failed`, or `sent`. Body of the response contains a JSON object with a single field:

    - `message_id` - List of identifiers of the messages of given `kind`.
    - `limit` -  Output limit for message_id (false for unlimited).
    - `total_count` - Count of list message_id.

Example
-------

To send an SMS with `curl` installed:

    $ curl -u lvv:SecretPAss -i -H "Content-Type: application/json; charset=UTF-8" -d '{"text":"Hi, Jack!", "mobiles":["79680000000", "79160000000"]}' http://127.0.0.1:5000/api/v1.0/sms/outgoing

Should result in:

    HTTP/1.0 201 CREATED
    Content-Type: application/json

    {
      "mobiles": {
        "79160000000": {
          "message_id": "f22f4f49-eb75-44d8-9690-7ac6d5b607a0",
          "response": "Ok"
        },
        "79680000000": {
          "message_id": "0be8248b-1711-4257-b766-18fcac2babcb",
          "response": "Ok"
        },
      },
      "parts_count": 1,
      "sent_text": "Hi, Jack!"
    }


To inquire about a sent SMS:

    $ curl -u lvv:SecretPAss -i -H "Content-Type: application/json; charset=UTF-8" http://127.0.0.1:5000/api/v1.0/sms/sent/83c201e0-c093-47ee-9ab1-e968cbc58446

Should result in:

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
      "From": "lvv",
      "Sent": "14-10-13 11:37:09",
      "To": "79160000000",
      "Modem": "GSM1",
      "IMSI": "230000000000000",
      "message_id": "83c201e0-c093-47ee-9ab1-e968cbc58446"
      "text": "Hi, Jack!",
    }

Using a wrong `message_id`:

    $ curl -u lvv:SecretPAss -i -H "Content-Type: application/json; charset=UTF-8" http://127.0.0.1:5000/api/v1.0/sms/sent/7b533050-d5a0-4b52-b8ba-f5d2ed42e630f

Should result in:

    HTTP/1.0 404 NOT FOUND
    Content-Type: application/json

    {
      "message: ": "Not found: http://127.0.0.1:5000/api/v1.0/sms/outgoing/7b533050-d5a0-4b52-b8ba-f5d2ed42e630f",
      "status: ": 404
    }

Listing all received messages:

    $ curl -u lvv:SecretPAss -i -H "Content-Type: application/json; charset=UTF-8" http://127.0.0.1:5000/api/v1.0/sms/sent/

Should result in:

    HTTP/1.0 200 OK
    Content-Type: application/json

    {
      "limit": 10000,
      "message_id": ["feabbf50-0a55-488e-af0c-026cd3a5d10d", "4935165a-606d-450e-ad91-0086483e4ecc"],
      "total_count": 2
    }

And that is all.
