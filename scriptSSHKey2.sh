TIME=$1
CAPITAO=$2
EMAIL=$3
CATEGORIA=$4
TIMECAT=$TIME$CATEGORIA
sudo adduser $TIMECAT
sudo chown -R $TIMECAT:$TIMECAT /home/$TIMECAT/
ssh-keygen -f $TIMECAT -t rsa -b 2048
sudo mkdir -p /home/$TIMECAT/.ssh
cat ${TIMECAT}.pub >> ./authorized_keys
sudo -E cp ./authorized_keys /home/${TIMECAT}/.ssh/authorized_keys
sudo -E chmod 600 /home/${TIMECAT}/.ssh/authorized_keys
mv $TIMECAT $TIMECAT.pem
sudo usermod -aG docker ${TIMECAT}
python3 vsskeyemail.py --categoria $CATEGORIA --time $TIME --email $EMAIL --capitao $CAPITAO
rm -rf ./authorized_keys
