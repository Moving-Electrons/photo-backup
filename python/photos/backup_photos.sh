# - nohup ignores HUP (hagup) signal. Meaning that it keeps the script 
# running even after the user disconnects from terninal.
# - 2>&1 redirects stderr to stdout, so no further interaction is needed
# after the script is called (which is handy when running the script remotely).
# - The final "&" runs the script in the background.
 
sudo nohup python3 backup_photos-hat.py "$1" >> ~/scripts/logs/backup_photos.output 2>&1  &

