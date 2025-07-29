FROM public.ecr.aws/lambda/python:3.12

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock  ${LAMBDA_TASK_ROOT}

# Install dependencies using uv
RUN uv sync

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.main.handler" ]