# committing to Github
echo "Filename: $1"
git add .
git commit -m "another commit !!!"
git push origin
sudo mn -c
sudo python3 "$1"
