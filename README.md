# facial-rigging-toolset

This toolset provides automations for facial rigging setup.

## Installation
Add "python" directory to PYTHONPATH environment variable.

## Usage
```python
import facial_rig_toolset.model_check as mcheck

# get model selection and store it in a global variable
mcheck.model_selection()

mcheck.auto_uvs()

```