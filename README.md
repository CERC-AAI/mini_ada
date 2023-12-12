
## About this project

- Create a small scale version of Ada that can be run on the Mila cluster with simple environments such as [BabyAI](https://www.notion.so/Chevalier-Boisvert-et-al-2018-4607b639c1b54218b60bffcf33c2d2fa?pvs=21) or [Crafter](https://www.notion.so/Stani-et-al-2022-42996a7351704a849e1735d372e2dd76?pvs=21) or [Procthor](https://www.notion.so/Deitke-et-al-2022-188494461b464ef8b850061f735d9c1a?pvs=21).
- We can use this to test out modifications to Ada.
    - In particular, we are interested in augmenting transformer architectures with memory:
        - [Memorizing transformers](https://www.notion.so/8469784287ff4ef597474177ce6d24e1?pvs=21)
        - [Retrieval-Augmented Reinforcement Learning](https://www.notion.so/Goyal-Bengio-2022-fcc8ff7a10bb442e80e0857ef8de7fc9?pvs=21)
        - [Discrete Key-Value Bottleneck](https://www.notion.so/a6de73986797420f9f342eec16403279?pvs=21)
    - And also getting a working version of Muesli set up (and ultimately distributed):
        - [Muesli](https://www.notion.so/2934eda190bb4aaca178447019c78e49?pvs=21)
     
## Main files in Minigrid

To run a test env just run from the Minigrid folder:

```python
python minigrid/manual_control.py
```

The CustomEnv is defined in Minigrid/minigrid/envs/customv1.py
We have OOP objects that work with CustomEnv defined in Minigrid/minigrid/core/world_object_custom.py
Finally, the code for generating new environments can be found in Minigrid/minigrid/templates

## Current Progress

Jonathan Lim wrote up a summary doc of [his finding on BabyAI](https://www.notion.so/Minigrid-BabyAI-4970e49e4c5e4f2588da9a938e517ca2?pvs=21)

Jonathan Lim is finishing up a set up for procedural generation in BabyAI/Minigrid that will allow us to define level layouts via spreadsheets and stitch them together using randomized procedural generation techniques.

We have added a custom environment to Minigrid that rewrites the core step function to allow for object oriented mechanic creation. Objects for this environment should extend the WorldObjCustom class, and have the added callbacks:

```python
def test_overlap(self, env: CustomV1Env, obj: WorldObj) -> bool:
        """Can this overlap with the given object? Assume this is symmetric"""
```

```python
def stepped_on(self, env: CustomV1Env, approach_position:Point) -> None:
        """Runs when agent is on the same tile as this object"""
```

```python
def do_pickup(self, env: CustomV1Env) -> None:
        """Runs when agent picks up this object"""
```

```python
def do_dropped(self, env: CustomV1Env) -> None:
        """Runs when agent drops this object"""
```

```python
def step(self, env: CustomV1Env) -> None:
        """Runs each environment step"""
```

Using these new callbacks we can produce a bunch of new mechanics. For example, a PushBox can be made that is pushed by the agent, but will stop when it hits walls, etc:
