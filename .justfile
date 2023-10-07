user    := "atareao"
name    := `basename ${PWD}`
version := `git tag -l  | tail -n1`

build:
    echo {{version}}
    echo {{name}}
    docker build -t {{user}}/{{name}}:{{version}} \
                 -t {{user}}/{{name}}:latest \
                 .

push:
    docker push {{user}}/{{name}} --all-tags

start:
    docker run --init \
               --rm \
               --detach \
               --name {{name}} \
               --publish 8000:8000 \
               {{user}}/{{name}}:latest
    docker logs {{name}} -f

stop:
    docker stop {{name}}
