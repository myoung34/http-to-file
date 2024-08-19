HTTP to File
============

Send it an a POST payload, it will transfer it to a file

```
$ docker build -t http_to_file .
$ docker run -it -p 3000:3000 \
  -e BIND_PORT=3000 \
  -e API_KEY=foo \
  -e FILE_DIR=/opt/wut \
  http_to_file
```

