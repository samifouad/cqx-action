# cqx-action

Score a repository on every pull request, and refuse the ones that make it
worse.

```yaml
name: cqx
on: [pull_request]

permissions:
  contents: read
  security-events: write   # so findings land on their own lines

jobs:
  score:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: samifouad/cqx-action@v1
```

That is the whole thing. On a pull request it scores the branch, scores the
commit the branch is based on, and fails when any category is worse than it
was. A score on its own says little — every project sits somewhere. The
direction is the part worth blocking on.

## What you get

**The job summary** carries the five category scores and how each one moved,
with a link to the commit on [cqx.bio](https://cqx.bio) for every rule, every
finding, and the code each one points at.

**The findings land on their lines.** With `security-events: write` the action
uploads SARIF, and each finding appears in the Files changed tab beside the
code it is about — not as a comment that grows on every push and that people
learn to scroll past.

**The check fails** when a category drops. Nothing else fails it by default:
an existing problem that neither grew nor shrank is not this pull request's
business.

## Inputs

| input | default | what it does |
|---|---|---|
| `version` | latest | which cqx to run, e.g. `v0.1.18` |
| `path` | `.` | the tree to score |
| `against` | the PR's base | a ref to compare against; `none` to score without comparing |
| `min-score` | — | also fail when any category falls below this, a floor on top of the ratchet |
| `config` | — | a `cqx.json` to score against; otherwise one is searched for upward |
| `sarif` | `true` | write the findings as SARIF |
| `upload-sarif` | `true` | upload it to code scanning |
| `summary` | `true` | write the scores to the job summary |
| `fail` | `true` | fail the job when the gate refuses; `false` reports only |

## Outputs

| output | what it is |
|---|---|
| `scores` | the category scores, as JSON |
| `passed` | `true` when nothing refused the change |
| `report` | path to the whole report as JSON |
| `sarif` | path to the SARIF file |
| `url` | where this commit can be read on cqx.bio |

## Starting out

A repository that has never been scored will have findings. That is the point,
and it is also why the default gate is a ratchet rather than a floor: the
score you start with is yours, and the only thing being asked is that it does
not get worse.

When you are ready to hold a line, add one:

```yaml
      - uses: samifouad/cqx-action@v1
        with:
          min-score: '70'
```

## Reporting without blocking

```yaml
      - uses: samifouad/cqx-action@v1
        with:
          fail: 'false'
```

The summary and the findings still appear; the check stays green. Worth a week
or two before turning it on.

## A shallow checkout

`actions/checkout` fetches one commit by default, so the base of the pull
request is usually not there. The action fetches it — one commit, cheap — and
says so in a warning if it still cannot find it. If you would rather not
depend on that:

```yaml
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
```

## What it installs

A single static binary, from the release bucket at `releases.cqx.bio`, picked
for the runner it is on and verified against the checksums published beside
it. No node, no container, no toolchain. The installer is the same one a
person runs:

```
curl -fsSL https://cqx.bio/install | sh
```

## Licence

Apache-2.0. cqx itself lives at [samifouad/cqx](https://github.com/samifouad/cqx).
