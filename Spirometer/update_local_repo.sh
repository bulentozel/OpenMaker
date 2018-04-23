#!/bin/sh

#  update_local_repo.sh
#  
#
#  Created by Bulent Ozel on 5/8/17.
#
cd /Users/bulentozel/OpenMaker/GitHub/OpenMaker/APP

cp /Users/bulentozel/OpenMaker/Deployments/Heroku/*.py .
cp /Users/bulentozel/OpenMaker/Deployments/Heroku/*.txt .
cp /Users/bulentozel/OpenMaker/Deployments/Heroku/Procfile .
cp /Users/bulentozel/OpenMaker/Deployments/Heroku/*.html .

cp /Users/bulentozel/OpenMaker/Deployments/Heroku/data/*.p ./data/.
cp /Users/bulentozel/OpenMaker/Deployments/Heroku/data/*.csv ./data/.

cp /Users/bulentozel/OpenMaker/Deployments/Heroku/LibOM/*.py ./LibOM/.

cp /Users/bulentozel/OpenMaker/Deployments/Heroku/flask_service/*.py ./flask_service/.
cp /Users/bulentozel/OpenMaker/Deployments/Heroku/flask_service/*.py ./flask_service/.
cp /Users/bulentozel/OpenMaker/Deployments/Heroku/flask_service/templates/*.html ./flask_service/templates/.
