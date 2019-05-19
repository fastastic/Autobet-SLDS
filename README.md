# Autobet-SLDS
OpenSource project for the SLDS subject.

## Installation of the environment
1. `sudo apt-get install python-pip firefox xvfb`
2. `sudo pip install pyvirtualdisplay selenium`
3. `wget https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-arm7hf.tar.gz`
4. `tar xzvf geckodriver-v0.23.0-arm7hf.tar.gz geckodriver`
5. `sudo mv geckodriver /usr/local/bin`
6. `sudo cp /usr/local/bin/geckodriver /usr/bin`

## Execution
`python3 autobet.py`
