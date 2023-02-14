.PHONY: clean style 

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete


## Apply formatting
style:
	black ./src
	isort ./src --profile black