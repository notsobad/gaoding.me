rsync -avz --delete -e ssh `pwd`/ vps:/home/notsobad/todolist/ --exclude '.git' --exclude '*.swp' --exclude 'up.sh' --exclude 'sessions/'
