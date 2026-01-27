# Homebrew Installation Guide

This guide explains how to install the Consciousness System Environment using Homebrew.

## Quick Start

### Installing from Homebrew Tap

To install using Homebrew, you need to add this repository as a "tap":

```bash
# Add the tap (this tells Homebrew where to find the formula)
brew tap DarkWinD90/Consciousness_Env https://github.com/DarkWinD90/Consciousness_Env

# Install the package
brew install consciousness-env
```

### Installing HEAD (Development Version)

To install the latest development version directly from the repository:

```bash
# Add the tap first (if not already added)
brew tap DarkWinD90/Consciousness_Env https://github.com/DarkWinD90/Consciousness_Env

# Install from HEAD
brew install --HEAD consciousness-env
```

## Using the Installed Package

After installation, the `consciousness` command will be available system-wide:

```bash
# Show version
consciousness version

# Run full integration simulation (Phase 7)
consciousness run

# Run a specific phase
consciousness run --phase 1
consciousness run --phase 2
# ... up to phase 7

# Run appendix simulations
consciousness appendix a          # Base simulation (Appendix A)
consciousness appendix base       # Same as above
consciousness appendix b          # System graph visualization (Appendix B)
consciousness appendix graph      # Same as above
consciousness appendix c          # Recursive reflection (Appendix C)
consciousness appendix reflection # Same as above

# Show help
consciousness --help
consciousness run --help
consciousness appendix --help
```

## Updating

To update to the latest version:

```bash
# Update Homebrew and upgrade the package
brew update
brew upgrade consciousness-env
```

For HEAD installations:

```bash
# Reinstall from the latest HEAD
brew reinstall --HEAD consciousness-env
```

## Uninstalling

To remove the package:

```bash
brew uninstall consciousness-env
```

To also remove the tap:

```bash
brew untap DarkWinD90/Consciousness_Env
```

## Troubleshooting

### Formula Not Found

If you get a "formula not found" error, make sure you've added the tap:

```bash
brew tap DarkWinD90/Consciousness_Env https://github.com/DarkWinD90/Consciousness_Env
```

### Python Version Issues

The formula requires Python 3.11. If you encounter issues, ensure Python 3.11 is installed:

```bash
brew install python@3.11
```

### Missing Dependencies

If simulations fail due to missing dependencies, try reinstalling:

```bash
brew reinstall consciousness-env
```

## For Developers

### Testing the Formula Locally

To test the formula without installing:

```bash
brew install --build-from-source Formula/consciousness-env.rb
```

### Creating a Release

When creating a release:

1. Tag the release in Git:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. Update the formula to use the release tarball instead of HEAD:
   ```ruby
   url "https://github.com/DarkWinD90/Consciousness_Env/archive/refs/tags/v1.0.0.tar.gz"
   sha256 "REPLACE_WITH_ACTUAL_SHA256"
   ```

3. Calculate the SHA256:
   ```bash
   curl -L https://github.com/DarkWinD90/Consciousness_Env/archive/refs/tags/v1.0.0.tar.gz | shasum -a 256
   ```

## Alternative Installation Methods

If you prefer not to use Homebrew, you can also install using:

### pip

```bash
pip install git+https://github.com/DarkWinD90/Consciousness_Env.git
```

### Manual Installation

```bash
git clone https://github.com/DarkWinD90/Consciousness_Env.git
cd Consciousness_Env
pip install -e .
```

## Support

For issues or questions, please visit:
https://github.com/DarkWinD90/Consciousness_Env/issues
