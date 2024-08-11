eval "$(ssh-agent -s)"
ssh-add ~/.ssh/activity-tracker
git pull $1
