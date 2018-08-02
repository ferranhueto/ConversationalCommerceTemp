#!/bin/bash

###### COMMAND TO CHECK IF A CERTAIN THING IS INSTALLED
# command -v foo >/dev/null 2>&1 || { echo >&2 "I require foo but it's not installed.  Aborting."; exit 1; }

if [[ "$OSTYPE" == "linux-gnu" ]]; then
    echo Operating system: Linux
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo "Detected Operating System: Mac OSX"
    echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    echo
    echo "===========> Alexa Environment Setup <==========="

    while true
    do
        read -p 'Would you like to setup the Alexa environment? (Y/n) ' answer
        echo

        case $answer in [yY]* )

            # Install Python 3.6.5
            curl -O https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tgz
            tar xf Python-3.6.5.tgz
            cd Python-3.6.5
            ./configure
            make
            make install

            # Install Pip
            # (If there are issues here, try uninstall and reinstalling pip via `pip uninstall pip`)
            curl -O https://files.pythonhosted.org/packages/ae/e8/2340d46ecadb1692a1e455f13f75e596d4eab3d11a57446f08259dee8f02/pip-10.0.1.tar.gz
            tar xvfz pip-10.0.1.tar.gz
            cd pip-10.0.1
            python3 setup.ppy install
            cd ..  # move back out of the pip-10.0.1 directory

            # Install virtualenv, create an environment
            pip install virtualenv
            virtualenv -p python3 alexa_venv
            # Don't need to activate the virtual environment
            # source /Users/agaidis/Auto-ID-Lab/ConversationalCommerce/alexa_venv/bin/activate

            # All packages (time, urllib, and json) should come default with Python3

            break;;

        [nN]* ) break;;
        *) echo "Input not recognized. Please type either \"Y\" or \"n\"."
        esac
    done

    echo
    echo "===========> VOSW2 Environment Setup <==========="

    while true
    do
        read -p 'Would you like to setup the VOSW2 environment? (Y/n) ' answer
        echo

        case $answer in [yY]* )

            # Install Python 2.7.15
            curl -O https://www.python.org/ftp/python/2.7.15/Python-2.7.15.tgz
            tar xf Python-2.7.15.tgz
            cd Python-2.7.15
            ./configure
            make
            make install
            cd ..  # move back out of the Python-2.7.15 directory

            # Install Pip
            # (If there are issues here, try uninstall and reinstalling pip via `pip uninstall pip`)
            curl -O https://files.pythonhosted.org/packages/ae/e8/2340d46ecadb1692a1e455f13f75e596d4eab3d11a57446f08259dee8f02/pip-10.0.1.tar.gz
            tar xvfz pip-10.0.1.tar.gz
            cd pip-10.0.1
            python setup.py install
            cd ..  # move back out of the pip-10.0.1 directory

            # Install virtualenv, create an environment
            pip install virtualenv
            virtualenv -p python2.7 vosw2_venv
            # activate the environment to download requirements
            source /Users/agaidis/Auto-ID-Lab/ConversationalCommerce/vosw2_venv/bin/activate
            pip install -r ./VOSW2/requirements.txt
            deactivate  # exit virtual environment

            break;;

        [nN]* ) break;;
        *) "Input not recognized. Please type either \"Y\" or \"n\"."
        esac
    done

    echo
    echo "=====>  DeepSpeech & Web Socket Server Environment Setup <====="

    while true
    do
        read -p 'Would you like to setup the Web Socket Server environment? (Y/n) ' answer
        echo

        case $answer in [yY]* )

            # Install brew
            /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

            # Install git-lfs and download the large files
            brew install git-lfs
            git lfs install
            git lfs pull

            # Install and use nvm (https://github.com/creationix/nvm) to get node version 8.11.3
            curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash

            export NVM_DIR="$HOME/.nvm"
            [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
            [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

            nvm install v8.11.3

            # Run npm install to download dependencies for websocket_server
            cd /Users/agaidis/Auto-ID-Lab/ConversationalCommerce/websocket_server/
            npm install
            cd ..

            break;;

        [nN]* ) break;;
        *) "Input not recognized. Please type either \"Y\" or \"n\"."
        esac
    done

    echo
    echo "======> Python Client Environment Setup <======"

    while true
    do
        read -p 'Would you like to setup the Python Client environment? (Y/n) ' answer
        echo

        case $answer in [yY]* )

            # Install Python 3.6.5
            curl -O https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tgz
            tar xf Python-3.6.5.tgz
            cd Python-3.6.5
            ./configure
            make
            make install
            cd ..

            # Install Pip
            # (If there are issues here, try uninstall and reinstalling pip via `pip uninstall pip`)
            curl -O https://files.pythonhosted.org/packages/ae/e8/2340d46ecadb1692a1e455f13f75e596d4eab3d11a57446f08259dee8f02/pip-10.0.1.tar.gz
            tar xvfz pip-10.0.1.tar.gz
            cd pip-10.0.1
            python3 setup.ppy install
            cd ..  # move back out of the pip-10.0.1 directory

            # Install virtualenv, create an environment
            #pip install virtualenv
            virtualenv -p python3 python_client_venv
            # Don't need to activate the virtual environment
            source /Users/agaidis/Auto-ID-Lab/ConversationalCommerce/python_client_venv/bin/activate
            pip3 install -r ./PythonClient/requirements.txt

            while true
            do
                read -p 'RPi.GPIO will only work on a Raspberry Pi. Will this be a Raspberry Pi Client? (Y/n) ' answer
                echo

                case $answer in [yY]* )

                    pip3 install RPi.GPIO==0.6.3

                    break;;

                [nN]* ) break;;
                *) "Input not recognized. Please type either \"Y\" or \"n\"."
                esac
            done

            deactivate

            break;;

        [nN]* ) break;;
        *) "Input not recognized. Please type either \"Y\" or \"n\"."
        esac
    done

elif [[ "$OSTYPE" == "cygwin" ]]; then
    # POSIX compatibility layer and Linux environment emulation for Windows
    echo Operating system: Cygwin
elif [[ "$OSTYPE" == "msys" ]]; then
    # Lightweight shell and GNU utilities compiled for Windows (part of MinGW)
    echo Operating system: Msys
elif [[ "$OSTYPE" == "win32" ]]; then
    echo Operating system: Windows32
elif [[ "$OSTYPE" == "freebsd"* ]]; then
    echo Operating system: FreeBSD
else
    echo Operating system unknown.
fi
