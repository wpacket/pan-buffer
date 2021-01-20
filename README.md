# pan-buffer
A script to spot buffer intensive sessions on your Palo Alto Network Firewall and avoid performance issues.
The script was tested with PAN-OS 10.0

## Explanation & Motivation
The script idea came with a performance issue I had on a production Palo Alto Network Firewall one day. The firewall itself was not the problem, at least it was properly sized for this environment. However, every once in a while I had specific sessions hitting my buffer so badly that legitimate traffic was impacted with delay & random drop. I had to find out what session was killing my performance even if I was not in front of my terminal.

## How does it work
The script will connect to the Firewall every 5s using the XML API and extract the following information.
- Session ID using more than 50% of the buffer.
- Information about the session ( source, destination, application )  
If an offending session is found, the script will log it. 

## How to Run it
```
python3 pan-buffer.py&
```

## Example
This example demonstrates how I was able to spot smbv2 session doing a massive backup ( several TB ) during the day and literally killing my buffer when doing the APP-ID detection.
```
# python3 pan-buffer.py&

# tail -f ./pan_buffer.log

2021-01-20 16:54: Session ID =20878  (Z_DMZ_PROD_18)172.17.21.33 -> (Z_SAN_FR)172.17.32.33:445 APP=ms-ds-smbv2
Packet Buffer Usage: 78%

2021-01-20 17:08: Session ID =20891  (Z_DMZ_PROD_18)172.17.21.33 -> (Z_SAN_FR)172.17.32.33:445 APP=ms-ds-smbv2
Packet Buffer Usage: 98%
....

```

## How to fix the problem once you spot it
If the traffic is legitimate, an application override rule might eventually fix the problem by offloading the APP-ID process.
If not, you can simply drop this traffic silently using a rule. 
Note that some options exist in PANOS to take care of this behavior natively ( Packet Buffer Protection ), however, they are applied at the Zone level and will concern every session traversing it.


