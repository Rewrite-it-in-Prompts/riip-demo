FROM public.ecr.aws/docker/library/alpine:3.20

# Install Python and pip
RUN apk add --no-cache python3 py3-pip

# Set up a virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ .

# Run unit tests
RUN python -m unittest discover -v < /dev/null

# Set the entry point
ENTRYPOINT ["python", "main.py"]