#!/bin/bash

if [[ "$OSTYPE" == "linux-gnu" ]]; then
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo "Detected Operating System: Linux"
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    # Start Docker daemon if not already started
    sudo service docker restart

    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
    sudo apt-get install git-lfs
    git lfs install
    git lfs pull

    ##### WEBSOCKET_SERVER IMAGE CREATION #####
    docker build -t websocket_server .

    ##### VOSW ORIGINAL IMAGE CREATION #####
    docker build -t vosw_original ./VOSW-2016-original/

    ##### VOSW2 IMAGE CREATION #####
    docker build -t vosw2 ./VOSW2/

    ##### PYTHON CLIENT IMAGE CREATION #####
    docker build -t python_client ./PythonClient/


elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo "Detected Operating System: Mac OSX"
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    # Start Docker daemon if not already started
    ./docker-start.sh

    # Install brew
    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    # Install git-lfs and download the large files
    brew install git-lfs
    git lfs install
    git lfs pull

    ##### WEBSOCKET_SERVER IMAGE CREATION #####
    docker build -t websocket_server .

    ##### VOSW ORIGINAL IMAGE CREATION #####
    docker build -t vosw_original ./VOSW-2016-original/

    ##### VOSW2 IMAGE CREATION #####
    docker build -t vosw2 ./VOSW2/

    ##### PYTHON CLIENT IMAGE CREATION #####
    docker build -t python_client ./PythonClient/


elif [[ "$OSTYPE" == "win32" ]]; then
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo "Detected Operating System: Windows"
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"

    echo "You need to make sure you install git-lfs and pull from the repository using `git lfs pull`"
    echo "Please see: https://github.com/git-lfs/git-lfs/wiki/Installation for more information."

    echo "Please make sure the Docker daemon is running."

    while true
    do
        read -p 'Is your Docker daemon running? (Y/n) ' answer
        echo

        case $answer in [yY]* )

            ##### WEBSOCKET_SERVER IMAGE CREATION #####
            docker build -t websocket_server .

            ##### VOSW ORIGINAL IMAGE CREATION #####
            docker build -t vosw_original ./VOSW-2016-original/

            ##### VOSW2 IMAGE CREATION #####
            docker build -t vosw2 ./VOSW2/

            ##### PYTHON CLIENT IMAGE CREATION #####
            docker build -t python_client ./PythonClient/

            break;;

        [nN]* ) break;;
        *) "Please start the Docker daemon and re-run this script."
        esac
    done

else
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo "Operating System Unkown"
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
fi
