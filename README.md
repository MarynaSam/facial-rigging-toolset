# facial-rigging-toolset

This toolset provides automations for facial rigging setup.

## Installation
Add "python" directory to PYTHONPATH environment variable.

## Usage
```python
import facial_rig_toolset.model_check as mcheck

mcheck.auto_uvs()

```
```python
from facial_rig_toolset import head_cut

# select the head faces you want to cut
head_cut.head_cut()

```