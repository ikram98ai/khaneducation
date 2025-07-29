FROM public.ecr.aws/lambda/python:3.12

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ${LAMBDA_TASK_ROOT}

# Install dependencies using uv sync with --system flag
WORKDIR ${LAMBDA_TASK_ROOT}
RUN uv sync --frozen --no-dev --system

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "app.main.handler" ]
