# u-connectXpress_azure_device_provisioning_services

## Disclaimer
Copyright &copy; u-blox 

u-blox reserves all rights in this deliverable (documentation, software, etc.,
hereafter “Deliverable”). 

u-blox grants you the right to use, copy, modify and distribute the
Deliverable provided hereunder for any purpose without fee.

THIS DELIVERABLE IS BEING PROVIDED "AS IS", WITHOUT ANY EXPRESS OR IMPLIED
WARRANTY. IN PARTICULAR, NEITHER THE AUTHOR NOR U-BLOX MAKES ANY
REPRESENTATION OR WARRANTY OF ANY KIND CONCERNING THE MERCHANTABILITY OF THIS
DELIVERABLE OR ITS FITNESS FOR ANY PARTICULAR PURPOSE.

In case you provide us a feedback or make a contribution in the form of a
further development of the Deliverable (“Contribution”), u-blox will have the
same rights as granted to you, namely to use, copy, modify and distribute the
Contribution provided to us for any purpose without fee.

## Azure IoT Hub device provisioning service

### Replace the following lines with your credentials and paths:

```
# Device configuration, change the following values accordingly:
SSID = "SSID"
PASSWORD = "PASSWORD"
iothubhostname = "global.azure-devices-provisioning.net"
registration_Id = "registration_Id"
idScope = "0ne0067E45C"
path_to_CA = "C:\\azure\\ca.pem"
path_to_Cert = "C:\\azure\\cert.pem"
path_to_key = "C:\\azure\\key.pem"
```

### Example output of a successful provisioning with NINA-W15 u-connectXpress and Extended Data Mode (EDM):


```
$ python .\azure_dps.py COM44
com44
com44 open
 18ms -> AT+UFACTORY
 400ms <- +STARTUP
AT+UFACTORY
OK
 401ms -> AT+CPWROFF
 416ms <- AT+CPWROFF
OK
 2804ms -> AT+USECMNG=0,0,ca.pem,1261
 3836ms <- AT+USECMNG=0,0,ca.pem,1261
>
 3836ms -> -----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
 5859ms <- +USECMNG:0,0,"ca.pem","ACB694A59C17E0D791529BB19706A6E4"
OK
 5860ms -> AT+USECMNG=0,1,cert.pem,1224
 6923ms <- AT+USECMNG=0,1,cert.pem,1224
>
 6923ms -> -----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
 8938ms <- +USECMNG:0,1,"cert.pem","9A1F95B8D512FA0ED075DD2B794ECB2A"
OK
 8941ms -> AT+USECMNG=0,2,key.pem,1704
 10033ms <- AT+USECMNG=0,2,key.pem,1704
>
 10034ms -> -----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
 12057ms <- +USECMNG:0,2,"key.pem","695D5D1EBB1DDBD0C6F2C128BAEB7F34"
OK
 12057ms -> ATO2
 12067ms <- ATO2
OK
 14076ms -> 0xAA00120044 'AT+UWSC=0,2,SSID\r' 0x55
 14089ms AT response: OK
 14091ms -> 0xAA00100044 'AT+UWSC=0,5,2\r' 0x55
 14105ms AT response: OK
 14106ms -> 0xAA001F0044 'AT+UWSC=0,8,PASSWORD\r' 0x55
 14121ms AT response: OK
 14122ms -> 0xAA000F0044 'AT+UWSCA=0,3\r' 0x55
 14153ms AT response: OK
 17017ms AT event: +UUWLE:0,802AA8035ADE,11
 17065ms AT event: +UUNU:0
 19092ms AT event: +UUNU:0
 22100ms -> 0xAA011F0044 'AT+UDCP=mqtt://global.azure-devices-provisioning.net:8883/?client=ninadps&user=0ne0067E45C/registrations/ninadps/api-version=2019-03-31&pt=$dps/registrations/PUT/iotdps-register/?$rid={request_id}&st=$dps/registrations/res/#&encr=3&keepAlive=60&ca=ca.pem&cert=cert.pem&privKey=key.pem\r' 0x55
 22440ms AT response: +UDCP:2
OK
 24712ms Connect event IPv4
        Channel id: 0
 25726ms AT event: +UUDPC:2,2,6,0.0.0.0,0,20.43.44.164,8883
 25726ms -> 0xAA002C0036 '\x00{"payload":"","registrationId":"ninadps"}' 0x55
 26168ms Data event:
        Channel id: 0
        Data: {"operationId":"5.b084dab098f0a900.076859d0-7180-40b8-9d06-bf611e398ec0","status":"assigning"}

 26169ms -> 0xAA00950044 'AT+UDUV=0,$dps/registrations/GET/iotdps-get-operationstatus/?$rid={request_id}&operationId=5.b084dab098f0a900.076859d0-7180-40b8-9d06-bf611e398ec0\r' 0x55
 26197ms AT response: OK
 26197ms -> 0xAA00CD0044 'AT+UDCP=mqtt://global.azure-devices-provisioning.net:8883/?client=ninadps&user=0ne0067E45C/registrations/ninadps/api-version=2019-03-31&pt=%%0&encr=3&keepAlive=60&ca=ca.pem&cert=cert.pem&privKey=key.pem\r' 0x55
 26234ms AT response: +UDCP:4
OK
 26235ms Connect event IPv4
        Channel id: 1
 27245ms AT event: +UUDPC:4,2,6,0.0.0.0,0,20.43.44.164,8883
 27245ms -> 0xAA00160036 '\x01get operationstatus' 0x55
 27466ms Data event:
        Channel id: 0
        Data: {"operationId":"5.b084dab098f0a900.076859d0-7180-40b8-9d06-bf611e398ec0","status":"assigned","registrationState":{"x509":{"enrollmentGroupId":"enrolGroup"},"registrationId":"ninadps","createdDateTimeUtc":"2022-07-04T08:28:35.8694014Z","assignedHub":"leoDPS.azure-devices.net","deviceId":"ninadps","status":"assigned","substatus":"initialAssignment","lastUpdatedDateTimeUtc":"2022-07-04T08:28:36.154464Z","etag":"IjYwMDA4OTJjLTAwMDAtMDEwMC0wMDAwLTYyYzJhNGI0MDAwMCI="}}

Successfully Assigned
 27468ms -> 0xAA000D0044 'AT+CPWROFF\r' 0x55
 27482ms AT response: OK
 ```
