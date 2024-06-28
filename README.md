## Setup Instructions obv

1. **Install pyenv** (if not already installed):
    ```bash
    curl https://pyenv.run | bash
    ```

    Add the following lines to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):
    ```bash
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    ```

    Restart your shell or run:
    ```bash
    source ~/.bashrc  # or source ~/.zshrc if using zsh
    ```

2. **Install the desired Python version** (e.g., Python 3.9.7):
    ```bash
    pyenv install 3.9.7
    ```

3. **Create a virtual environment** for your project:
    ```bash
    pyenv virtualenv 3.9.7 fastapi-env
    ```

4. **Set the local Python version** for your project to the virtual environment:
    ```bash
    pyenv local fastapi-env
    ```

    This will create a `.python-version` file in your current directory, specifying the virtual environment to use.

5. **Install FastAPI and Uvicorn** in the virtual environment:
    ```bash
    pip install fastapi uvicorn
    ```

6. **Create a `requirements.txt` file** for your project (optional, but recommended for reproducibility):
    ```bash
    pip freeze > requirements.txt
    ```

7. **Activate the virtual environment** whenever you work on the project:
    ```bash
    pyenv activate fastapi-env
    ```

Here’s a summary of the commands you’ll run:

```bash
# Step 1: Install pyenv (if not already installed)
curl https://pyenv.run | bash

# Add the following to your shell profile (e.g., ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Restart shell or source profile
source ~/.bashrc  # or source ~/.zshrc if using zsh

# Step 2: Install the desired Python version
pyenv install 3.9.7

# Step 3: Create a virtual environment for your project
pyenv virtualenv 3.9.7 fastapi-env

# Step 4: Set the local Python version for your project
pyenv local fastapi-env

# Step 5: Install FastAPI and Uvicorn
pip install fastapi uvicorn

# Step 6: Create a requirements.txt file
pip freeze > requirements.txt

# Step 7: Activate the virtual environment
pyenv activate fastapi-env
```

Now you can work on your FastAPI project within the isolated virtual environment. To run your FastAPI application, use:

```bash
uvicorn main:app --reload
```