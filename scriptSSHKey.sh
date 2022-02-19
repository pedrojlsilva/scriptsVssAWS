TIME=$1
CAPITAO=$2
EMAIL=$3
CATEGORIA=$4
sudo adduser $TIME
sudo chown -R $TIME:$TIME /home/$TIME/
ssh-keygen -f $TIME -t rsa -b 2048
sudo mkdir -p /home/$TIME/.ssh
cat ${TIME}.pub >> ./authorized_keys
sudo -E cp ./authorized_keys /home/${TIME}/.ssh/authorized_keys
sudo -E chmod 600 /home/${TIME}/.ssh/authorized_keys
TIMECAT=$TIME$CATEGORIA
mv $TIME $TIMECAT.pem
sudo usermod -aG docker ${TIME}
python3 vsskeyemail.py --categoria $CATEGORIA --time $TIME --email $EMAIL --capitao $CAPITAO
