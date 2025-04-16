The project is divided into two pieces :

## The first is an attempt to connect to Travian the "organic" way with Selenium.
This attempt is for now abandonned. The idea was to use a browser to connect to Travian and then replicate
a specific path using the Selenium plugin (works only on firefox these days) to for example launch the raid lists in Travian.

## The second is a  classic attempt by reverse engineering logins with burpsuite/inspect, storing variables and making API requests

Login.py :
As of now, store your variables in a .env file (TRAVIAN_EMAIL and TRAVIAN_PASSWORD). My script will then log in to Travian using the PKCE flow and retrieve the GraphQL response containing your active avatars and the servers they belong to. You will then be able to indicate to which of your servers you wish to login to from the list you will be served in the terminal.

