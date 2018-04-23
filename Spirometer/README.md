<img src="https://github.com/openmaker-eu/socialmedia/blob/master/OpenMakerLogo.png" height="128"><img src="./figures/uzh_logo.png" height="100"><img src="https://github.com/openmaker-eu/socialmedia/blob/master/Ekran%20Resmi%202017-01-11%2014.34.43.png" height="128">

# Spirometer: The OpenMaker Opinion Leaders API

This API is a prototype of a feature where OM-DSP users could be able to detect and explore the opinion leaders within the maker community.

The feature provided by this API could also enable the DSP leaders or accelerators to explore and follow other makers with specific non-technical concerns or focuses.

The API may enable the accelerators or other users of the DSP to check any Tweeter user's 'influence' on open-making related non-technical themes as well as be able to see their possible position on the opinion score board. 

The API connects to the WatchTower APP and retrieves the list of influencers. It also connects to Twitter API to retrieve tweets of the designated influencers. It analyzes the textual contents of the latest tweets of the WatchTower influencers' as well as any other designated Twitter user.

The APP has both a graphical (GUI) and a programming interface (API). Both interfaces are deployed on the OpenMaker InSight server. They can however be run on local computer.

# A. Spirometer GUI prototype
The GUI prototype is developed for demonstrational purposes. It aims to present ideas about how data provided by the API can be used for a better user experience.

## 1. GUI: OpenMaker Community Spirometer offline datastatic version
In order to play with the GUI **first download this repo** and then open the file [spirometer.html](./spirometer.html) with your preferred browser. However, note that this is a datastatic version, that is, it doesn't connect to the OpenMaker WatchTower or Twitter for new queries and new profiling.

## 2. GUI: OpenMaker Community Spirometer online version

### i) Online static data version:
The online data static version is served at follwing link. It uses previously harvested and analyzed data: 
 * [http://178.62.229.16:5000/gui/datastatic](http://178.62.229.16:5000/gui/datastatic)

### ii) Online live data version:
The live version can be used to query and discover additional Twitter user profiles on the OpenMaker spirals:
 * [http://178.62.229.16:5000/gui](http://178.62.229.16:5000/gui)
 
 There any twitter user can be queried:
 ````
 http://178.62.229.16:5000/gui/<aValidTwitterUserName>
 ````
 Such as [http://178.62.229.16:5000/gui/bulentozel](http://178.62.229.16:5000/gui/bulentozel)
 
 Please note that in the current version the total number of additional queries that can be placed within a half an hour is limited by by Twitter API. 

# B. Notebook
A Jupyter notebook on the functionalities and modules of APP itself can be accessed [hereby](./OMLeaders.ipynb)

# C. Installing and running the APP on a local computer

After having created the python environment using the [requirements file](./requirements.txt), run the python script which is given via this repository.

Check follwing guides for creation of pyhton environments: 
- http://stackoverflow.com/questions/7225900/how-to-pip-install-packages-according-to-requirements-txt-from-a-local-directory
- http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/

Once the repository installed on a local computer, see [requirements.txt](./requirements.txt), replace the "http://178.62.229.16:5000/" part of the URL below with http://127.0.0.1:5000/
 
````
python run_wsgi.py
````
 

# C. The Spirometer API Version

In the current version data from the API can be retrieved by simple HTTP requests. The service is a typical RESTful application developed by a WSGI Framework (Flask + Gunicorn). 

In order to query categories and memes available via API:
````
curl http://178.62.229.16:5000/
````
which returns the list of available category/memes spirals in JSON format:
````
{
  "categories": [
    "openness", 
    "sharing", 
    "innovation", 
    "sustainability", 
    "collectiveness"
  ], 
  "status": "OpenMaker.EU meme analysis server is UP."
}
````
### 1. Retrieving the list of opinion leaders

####  Retrieving the list of overall opinion leaders on OpenMaking: 
The root entry point below returns a combined score:
````
curl http://178.62.229.16:5000/scoreboard
````
 A typical response as JSON object is as follows:
 
 ````
 {
  "rankings": [
    {
      "score": 2.7688442211055277, 
      "username": "makerbot"
    }, 
    {
      "score": 2.5376884422110555, 
      "username": "arduinoblog"
    }, 
    {
      "score": 1.964824120603015, 
      "username": "linuxfoundation"
    }, 
    ...
    {
      "score": 0.2268041237113402, 
      "username": "Pi_Borg"
    }
  ], 
  "type": "openmakership"
}
````

The score at the moment is generated using a built-in dictionary, where a predetermined keywords and phrases are matched to categories. The app aims to maximize accuracy and retrieval at detecting the predetermined expresions within the texts that are generated by an influencer. Right now, it scans the tweets of the user as input texts in order to detect themes within them and map the themes to the categories.

#### Retrieveing the list of opinion leaders on a specific theme:

The general structure in order to access to a specific board is as follows:

````
http://178.62.229.16:5000/scoreboard/<category>
````
where for the current version it can be one of these:
````
<category>:{"openness","sharing","innovation","sustainability", "collectiveness"}
````

For instance, in order to retrieve the scoreboard of the sustainability debators. Here sustainability refers to discussions/tweets on environmental sustainability issues. 

````
curl http://178.62.229.16:5000/scoreboard/sustainability
````

The response is a JSON document: 

````
{
  "rankings": [
 
    {
      "score": 0.06976744186046512, 
      "username": "paulklint"
    }, 
    {
      "score": 0.04020100502512563, 
      "username": "linuxfoundation"
    }, 
   
   ...
     
    {
      "score": 0.005, 
      "username": "lifehacker"
    }
  ], 
  "type": "sustainability"
}
````



### 2. Checking overall score of an influencer

The API provides a query option to be able retrieve the score of a particular influencer determined by the WatchTower APP or any other Tweeter user of interest to the user:
A request:
````
http://178.62.229.16:5000/influencer/instructables
````
The response:
````
{
  "compositions": {
    "innovation": 0.14754098360655737, 
    "making": 0.5081967213114754, 
    "openness": 0.00546448087431694, 
    "sharing": 0.01639344262295082, 
    "sustainability": 0.02185792349726776
  }, 
  "influencer": "instructables", 
  "ntweets": 183, 
  "openmakership": 0.6994535519125683
}
````

Following query retrieves the score of a possible opinion leader who was not detected via the Watcher API:

````
curl http://178.62.229.16:5000/influencer/indy_johar
````

````
{
  "compositions": {
    "collectiveness": 0.025510204081632654, 
    "innovation": 0.08163265306122448, 
    "making": 0.3979591836734694, 
    "openness": 0.04591836734693878, 
    "sharing": 0.025510204081632654, 
    "sustainability": 0.025510204081632654
  }, 
  "influencer": "indy_johar", 
  "ntweets": 196, 
  "openmakership": 0.6020408163265306
}
````

It should be noted that any tweeter username can be queried by following pattern:

````
curl http://178.62.229.16:5000/influencer/<username>
````


