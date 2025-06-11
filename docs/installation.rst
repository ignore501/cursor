Installation
============

Requirements
-----------

* Python 3.10 or higher
* pip (Python package installer)
* Git

Installation Steps
----------------

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/yourusername/ronin-tg-app.git
      cd ronin-tg-app

2. Create and activate a virtual environment:

   .. code-block:: bash

      # For Windows
      python -m venv venv
      venv\Scripts\activate

      # For Linux/Mac
      python -m venv venv
      source venv/bin/activate

3. Install dependencies:

   .. code-block:: bash

      pip install -r requirements.txt

4. Create a .env file:

   .. code-block:: bash

      cp .env.example .env

5. Edit the .env file with your settings:

   .. code-block:: text

      TELEGRAM_TOKEN=your_bot_token_here
      DB_PATH=bot.db
      NOTEBOOKS_DIR=notebooks
      LOGS_DIR=logs

Development Setup
---------------

For development, install additional dependencies:

.. code-block:: bash

   pip install -r requirements-dev.txt

This will install:

* Testing tools (pytest, pytest-cov)
* Linting tools (black, isort, flake8, mypy)
* Documentation tools (sphinx)
* Security tools (safety, bandit)

Running Tests
-----------

.. code-block:: bash

   pytest

Generating Documentation
----------------------

.. code-block:: bash

   cd docs
   make html

The documentation will be available in ``docs/_build/html/``. 