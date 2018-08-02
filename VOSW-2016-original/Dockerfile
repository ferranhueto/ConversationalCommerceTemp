# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory to /VOSW-2016-original
WORKDIR /VOSW-2016-original

# Copy the current directory contents into the container at /VOSW-2016-original
ADD . /VOSW-2016-original

# Putting a variables in the environment
ENV SECRET_KEY="XXXXXXXXXXX"
ENV dbx_access_token=""

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD ["python", "app.py", "--host=0.0.0.0"]
