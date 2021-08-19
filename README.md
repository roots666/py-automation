## PY-scripts

### Installation:
```
git clone \
  --depth 1  \
  --filter=blob:none  \
  <this_git_project_url> \
;
cd aws-scripts

pip3 install -r requirements.txt # better to use virtual env though 
```
### Usage
#### manage_ec2.py

Script for stop,start,reboot aws ec2 instances by Tag and Regex

```
manage_ec2.py -h       
usage: manage_ec2.py [-h] -a ACTION_WITH_EC2 [-t TAG] -f FILT [-d]
                     [-l LOGLEVEL]

optional arguments:
  -h, --help            show this help message and exit
  -a ACTION_WITH_EC2, --action ACTION_WITH_EC2
                        Action with ec2 instance (start,stop,reboot). Use
                        like: -a stop
  -t TAG, --tag TAG     Tag for search. Use like: -t mytag
  -f FILT, --filter FILT
                        Filter(regex) for instances. Use like: -f
                        "aws-jenk-slave[0-5][0-9]"
  -d, --dryrun          Run ec2 action only in "dryrun" mode
  -l LOGLEVEL, --loglevel LOGLEVEL
                        Sets the threshold for logger
                        level(CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET). Use
                        like: -l INFO

```

### Examples
#### manage_ec2.py

- Start ec2 instances with tag "Name" and regex "aws-jenk-slave[0-5][0-9]"

```
./manage_ec2.py -a start -t Name -f "aws-jenk-slave[0-5][0-9]" -l INFO
```

### Usage
#### get_offline_nodes_and_poweroff.py

Script for get jenkins idle and offline slaves and poweroff via boto3 lib

```
./get_offline_nodes_and_poweroff.py -husage: get_offline_nodes_and_poweroff.py [-h] [-lbl LABELS [LABELS ...]]
                                         [-j_url J_URL] [-a] [-u USERNAME]
                                         [-p PASSWORD] [-d] [-l LOGLEVEL]

optional arguments:
  -h, --help            show this help message and exit
  -lbl LABELS [LABELS ...], --labels LABELS [LABELS ...]
                        Jenkins node(s) labels for parse. Use like: -j lbl1
                        lbl2 lblX
  -j_url J_URL, --jenkins_url J_URL
                        Jenkins url. Use like: -j_url
                        http://jenk-fake.net:8080
  -a                    Enable authentification for Jenkins
  -u USERNAME, --username USERNAME
                        Jenkins username
  -p PASSWORD, --password PASSWORD
                        Jenkins password
  -d, --dryrun          Run ec2 stop action only in "dryrun" mode
  -l LOGLEVEL, --loglevel LOGLEVEL
                        Sets the threshold for logger
                        level(CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET). Use
                        like: -l INFO

```

### Examples
#### get_offline_nodes_and_poweroff.py

```
./get_offline_nodes_and_poweroff.py -lbl mylovelylabel1 mylovelylabel2 -j_url http://jenk-fake.net:8080 -a -u user.name -p MySecurePass -l INFO

```