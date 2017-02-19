from setuptools import setup

setup(name="octets",
      py_modules=["octets"],
      install_requires=["six"],
      extras_require={
          "dev": ["coverage", "hypothesis", "pytest", "tox"],
      })
