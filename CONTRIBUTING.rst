You may contribute to Ordia. 

The software is developed under the Apache License, see the LICENSE file.
Any contributions to Ordia is assumed to be under the Apache License.

Ordia uses style checking and testing. This is handle via tox. 
Before issueing a pull request, install and execute tox in the main directory
of Ordia and ensure that no error is reported. 

The technology stack is Python with Flask, HTML, JavaScript, CSS and SPARQL
with queries to the Wikidata Query service. For now we attempt to be compatible
with both Python 2 and Python 3.

Any assets should be served from Ordia itself due to privacy.

Installation can be done by cloning the GitHub repository.

You might need to install requirements. In the main Ordia directory execute: 

pip install -r requirements.txt 

You can run an Ordia test service locally calling the `app.py` in the main
Ordia directory.

python app.py 

