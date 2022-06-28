import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="slurm-tools-quinoah",
    version="0.0.1",
    author="quinoah",
    author_email="noah.toyonaga@gmail.com",
    description="Tools for launching jobs on slurms",
    url="https://github.com/noahyt/slurm_tools",
    project_urls={
        "Bug Tracker": "https://github.com/noahyt/slurm_tools/isues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    entry_points={
        'console_scripts': [
            'launch-python-jobs-array = slurm_tools.launch_python_jobs_array:main',
        ]
    },
    python_requires=">=3.6",
)
