eval "$(ssh-agent -s)"
ssh-add ~/.ssh/activity-tracker
sudo hwclock -s
git push $1
