The project is divided into two pieces :

## The first is an attempt to connect to Travian the "organic" way with Selenium.
This attempt is for now abandonned. The idea was to use a browser to connect to Travian and then replicate
a specific path using the Selenium plugin (works only on firefox these days) to for example launch the raid lists in Travian.
It worked but ignore it. It's slow and I can't easily generalise it.

## The second is a  classic attempt by reverse engineering logins with burpsuite/inspect, storing variables and making API requests

login.py :
As of now, store your variables in a .env file (TRAVIAN_EMAIL and TRAVIAN_PASSWORD). My script will then log in to Travian using the PKCE flow and retrieve the GraphQL response containing your active avatars and the servers they belong to. You will then be able to indicate to which of your servers you wish to login to from the list you will be served in the terminal.

Currently, my main script (once you add your TRAVIAN_EMAIL and TRAVIAN_PASSWORD to the .env)
1) Logins to the main Travian dashboard
2) Provide you a list of your current created servers and let you choose
3) Provide you a list of your villages and let you choose
4) Provide you a list of the raiding lists of the village
5) It will iterate through the raiding list and identify which oasis do not have troops defending it

I was stuck for a while because travian devs use a checksum to protect from bots sending attacks via the attack flow. However check_sum_attack_breaking is 
a proof of concept that my script can extract it and pretend to be a human :D 
Next step is to integrate this to the MAIN script, make a few modular functions and we :

should have a script that parses through oases from your list and sends troops only to unprotected oases.
then have another script to launch your village raid lists.

Then I want a script to launch the hero at an appropriately weak oasis (which means querying hero health and status and calculations to identify what's "weak")

Afterwards, I want to build the oasis list myself by having an actual grid search around the village to be systematic and reduce human labour. 
