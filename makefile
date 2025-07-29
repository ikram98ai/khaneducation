sync:
	uv sync
lint:
	uv run ruff check

fix:
	uv run ruff check --fix

format:
	uv run ruff format

test:
	uv run pytest test_main.py

migrate:
	uv run alembic revision --autogenerate -m "auto_$(shell date +%s)_$(m)" && uv run alembic upgrade head

adminuser:
	uv run python create_admin.py -u="$(u)" -e="$(e)"

dev: 
	uv run fastapi dev app/main.py



tf_backend:
	@echo "Create S3 bucket for Terraform state"
	aws s3 mb s3://terraform-state-20250610

	@echo "Create DynamoDB table for state locking"
	aws dynamodb create-table \
		--table-name terraform-state-lock \
		--attribute-definitions AttributeName=LockID,AttributeType=S \
		--key-schema AttributeName=LockID,KeyType=HASH \
		--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

deploy:
	@echo "Deploying to AWS Lambda..."
	terraform -chdir=terraform init
	terraform -chdir=terraform plan -var="gemini_api_key=${GEMINI_API_KEY}" 
	terraform -chdir=terraform apply -var="gemini_api_key=${GEMINI_API_KEY}" 
	
destroy:
	@echo "Destroying AWS resources..."
	terraform -chdir=terraform destroy -var="gemini_api_key=${GEMINI_API_KEY}"  -lock=false

