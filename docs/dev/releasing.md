# Releasing

- **`release` branch owns the version.** Every push to `master` auto-bumps the patch, tags it, and ships docker (`master-push.yml` -> `release.yml`).
- **`master` version files are `0.0.0` placeholders.** Never hand-edit `package/version`, `kmir/pyproject.toml`, or `kmir/uv.lock`. They only ever hold `0.0.0`. So `kmir --version` is `0.0.0` on a local master build, and the real version in nix/docker builds.
- **Want minor/major instead of patch?** Put a trailer on its own line in a commit (or the squash/PR description) that lands on master e.g.:

  ```
  Bump: minor
  ```

  `major` > `minor` > `patch`; anything else defaults to patch.
