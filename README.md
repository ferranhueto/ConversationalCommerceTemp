# ConversationalCommerce

This repository contains projects created by the MIT Auto-ID Laboratory in order to further the exploration and standardization of conversational commerce. Below we outline each of the projects that are found in a subdirectory of this repository. To begin, we outline how to setup the appropriate environment for each project using Docker.
____________

## Docker

### General Information

All environments in the repository are managed by docker. Each project is built from a separate image and is thus run in a separate container. There are multiple Dockerfiles corresponding to different projects. The majority of these Dockerfiles reside in the project directory along with a `requirements.txt` file, however there are Dockerfiles that need access to multiple directories and these reside in the root directory.

### Downloading Docker

In order to get started with our environments, you must have Docker Community-Edition installed. To do this, please visit [this link](https://www.docker.com/community-edition).

### Image Creation

To build the images for all projects, run:

``` bash
./docker-images-setup.sh
```
Support for Windows is limited. For more details regarding the installation and setup of environments for Windows, please open `docker-images-setup.sh` and read the inline comments.

### Container Creation

Once the script above is done running, all the docker images should be built and containers are ready to be run. The following are the commands to create containers from the previously made images.

**Note:** The `-d` flag runs the container in the background. If you would like to run it in the foreground, remove this flag.

###### VOSW-2016-original

``` bash
docker run -i -t -p 8000:8000 -d vosw_original
```

###### VOSW2

``` bash
docker run -i -t -p 8000:8000 -d vosw2
```

###### PythonClient

``` bash

```

###### websocker_server

``` bash

```

All the environments should now be set-up and ready to rumble!

### Destroying Images and Containers

To remove all images and containers and perform an "environment cleanup", run:

``` bash
./docker-destory-all.sh
```

### Additional Information and Troubleshooting

For additional information and troubleshooting, please visit the documentation Docker provides at [this link](https://docs.docker.com/).

----------

## PythonClient

### Project Summary


----------

## websocket_server

### Project Summary

----------

## VOSW-2016-Original

### Project Summary

----------

## VOSW2

### Project Summary

----------

## WikiScraping

### Project Summary

We started this project to explore putting a voice interface into a practical web application. Once the server is running, `scrape.html` can be opened in a web browser, and Wikipedia articles can be searched for via voice. Once an article is found that matches what the user said, the text of the article is read aloud by the computer.   

----------

## Webpage2

### Project Summary

This showcases several uses deepspech has when integrated into webbrowsers. We can turn a light on and off on one webpage, and can use our voice to search wikipedia on the other.
----------

## idServerStuff

### Project Summary

This project is an extension of the existing client-server setup for the deepspeech speech to text setup.  Here the client has been modified to send additional information that won't be process as speech to the server.  The most recent iteration involves an RFID scanner that send infomation about who scanned their rfid card back to the server, in order to identify the speaker.
