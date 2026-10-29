# Profile illustration rotation

The scheduled workflow chooses one light and one dark illustration at minute 17
of each hour. It updates only the marked picture block in the profile README
and commits that file using GitHub's built-in token. No separate server,
package installation or custom secret is required.

The eight selected illustrations are listed in `scripts/rotate_illustrations.py`:
six light options and two dark options. The previous image is excluded from each
selection; the two dark options therefore alternate. The fallback image always
matches the selected light option. Existing GIF files are never rewritten.

Local checks and a single local rotation:

```sh
python3 -B -m unittest discover -s .github/scripts -p 'test_*.py'
python3 -B .github/scripts/rotate_illustrations.py
```

The workflow runs only after it exists on the repository's default branch, with
Actions enabled and permission for its token to write repository contents. It
uses a normal push; a protected branch or a concurrent change can reject that
push safely, and a later scheduled run starts from the current branch again.
There are no push or pull-request triggers and no CI-suppression flags.

GitHub may delay scheduled runs; this is hourly rotation rather than a change
on every page view. Visitors' caches may delay the visible update. GitHub can
disable schedules after 60 days without repository activity.
