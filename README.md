# AndrewVerify
Utility to verify CMU affiliation concurrently through request to Andrew Directory

## Possible Verification Format

### Indexed/Unindexed line-seperated Chinese-name/English-name/andrewID entries

```
1. 朱楚彦
2. Philip Zhu
3. Wenli Xiao
```

```
cyzhu
wlxiao
```

## Simple usage
Pass file path with data to be verified as arguments or directly pass data to be verified to stdin.

```bash
pip install -r requirements.txt
python run.py name_list.txt
```
