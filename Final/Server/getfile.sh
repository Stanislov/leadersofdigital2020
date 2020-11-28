
#!/bin/bash
source /root/anaconda3/bin/activate production_ml_env
cd /root/DL/
echo HELLLOO
echo $1
python3 getfile.py $1

