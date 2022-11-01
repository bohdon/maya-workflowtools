# Maya Attribute Resetter

A simple util for quickly resetting transform or other node attributes to their defaults in Maya.

Resetter is most useful in animation workflows, where you often want to reset a control to its default state without having to type in 0s and 1s in the channel box. Any transform node can be reset to its "zeroed-out" state without any setup, and special attributes (such as IKFK blend attributes) can have their default values stored on the node so that they are also restored when resetting a node to its default state.


## Setup

Run the following to launch the Resetter GUI:

```python
import resetter
resetter.GUI()
```

## Main Commands

Here are some of the main commands that make useful shelf buttons or hotkeys.

```python
import resetter

# store the selected nodes current keyable values as their defaults
resetter.setDefaults()

# reset selected nodes using defined defaults or basic transform defaults
resetter.reset()

# reset selected nodes using only defined defaults
resetter.reset(useBasicDefaults=False)
```
