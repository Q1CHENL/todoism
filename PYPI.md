# Build, Install, and Upload a Python Package to PyPI

## Built files

- `your_project-1.0.0.tar.gz`: Archive of the raw source code.

- `your_project-1.0.0-py3-none-any.whl`: Pre-built, ready-to-install package

- When running `pip install your_project`, `pip` prefers wheels over source distributions.

## Build the Project

`python -m build`

- Build and outputs a source distribution (.tar.gz) and a wheel (.whl) in the "dist/" directory.

## Install Locally (Editable Mode)

`pip install -e .`

- Installs the project in editable mode.

- Instead of copying your project's files into the Python site-packages/ folder (normal behavior), it creates a link (specifically a .egg-link file) that points back to your source directory.

- Changes to the project files are reflected immediately without reinstalling.

## Upload to PyPI

- `twine upload dist/*` to upload all files in the "dist/" directory.

- `twine upload dist/your_project-1.0.0*` to upload a specific version (usallly we upload both `.tar.gz` and `.whl`).

## Additional Notes

- Validate the built packages before uploading:
  twine check dist/\*
