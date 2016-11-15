sudo apt-get update
sudo apt-get install -y python-pip
sudo wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python
sudo pip install awscli --ignore-installed six
sudo pip install boto3
python setup.py install
