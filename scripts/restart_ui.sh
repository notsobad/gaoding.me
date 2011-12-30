ps aux|grep 'ui.py 8080 fcg[i]' | tr -s ' ' | cut -d ' ' -f2 | xargs --no-run-if-empty kill -3
cd /home/notsobad/todolist/ && \
python  /home/notsobad/todolist/ui.py 8080 fcgi >/dev/null 2>&1 &
