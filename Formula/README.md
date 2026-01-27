# Homebrew Formula for Consciousness_Env

This directory contains the Homebrew formula for installing the Consciousness System Environment.

## What is a Homebrew Formula?

A Homebrew formula is a Ruby script that tells Homebrew how to install software on macOS and Linux. This formula enables users to install the Consciousness_Env system using the Homebrew package manager.

## Using This Formula

### Installation

To install using this formula:

```bash
# Add this repository as a Homebrew tap
brew tap DarkWinD90/Consciousness_Env https://github.com/DarkWinD90/Consciousness_Env

# Install the package (HEAD version - latest development code)
brew install --HEAD consciousness-env
```

### What Gets Installed

The formula installs:
1. The `consciousness` command-line tool
2. All Python dependencies (numpy, matplotlib, networkx, scipy)
3. All simulation phases and appendices
4. Core modules and utilities

### Installation Location

Homebrew installs the package in:
- **Binaries**: `/usr/local/bin/consciousness` (on Intel Macs) or `/opt/homebrew/bin/consciousness` (on Apple Silicon)
- **Python Environment**: In a dedicated virtualenv managed by Homebrew

## Formula Details

### Key Features

- **Python Version**: Requires Python 3.11
- **Installation Method**: Uses `virtualenv_install_with_resources` to create an isolated Python environment
- **Dependencies**: Automatically installs all dependencies from `requirements.txt`
- **Testing**: Includes a test to verify the installation works

### Current Configuration

The formula currently installs from **HEAD** (the latest development version). This means:
- Users always get the latest features and fixes
- No need to create releases for users to get updates
- Users can update with `brew reinstall --HEAD consciousness-env`

### Migrating to Stable Releases

To switch to stable releases in the future:

1. Create a Git tag for the release:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

2. Update the formula to reference the release:
   ```ruby
   url "https://github.com/DarkWinD90/Consciousness_Env/archive/refs/tags/v1.0.0.tar.gz"
   sha256 "your_calculated_sha256_here"
   ```

3. Calculate the SHA256 hash:
   ```bash
   curl -L https://github.com/DarkWinD90/Consciousness_Env/archive/refs/tags/v1.0.0.tar.gz | shasum -a 256
   ```

4. Remove or comment out the `head` line if you want to make the stable release the default

## Testing the Formula

To test changes to the formula locally:

```bash
# Install from the local formula file
brew install --build-from-source Formula/consciousness-env.rb

# Or reinstall if already installed
brew reinstall --build-from-source Formula/consciousness-env.rb
```

## Troubleshooting

### Common Issues

1. **Formula not found**: Make sure you've added the tap first
   ```bash
   brew tap DarkWinD90/Consciousness_Env https://github.com/DarkWinD90/Consciousness_Env
   ```

2. **Python version issues**: Ensure Python 3.11 is installed
   ```bash
   brew install python@3.11
   ```

3. **Installation fails**: Try cleaning and reinstalling
   ```bash
   brew cleanup consciousness-env
   brew install --HEAD consciousness-env
   ```

## For Developers

### Formula Structure

```ruby
class ConsciousnessEnv < Formula
  include Language::Python::Virtualenv  # Use Python virtualenv helper

  desc "..."           # Short description
  homepage "..."       # Project homepage
  head "...", branch:  # Git repository and branch for HEAD install

  depends_on "python@3.11"  # Python dependency

  def install
    virtualenv_install_with_resources  # Install with dependencies
  end

  test do
    system bin/"consciousness", "version"  # Test installation
  end
end
```

### Best Practices

1. Keep dependencies minimal and let Python handle most of them
2. Use `virtualenv_install_with_resources` for automatic dependency management
3. Include a meaningful test that verifies the installation
4. Keep the formula simple and maintainable

## More Information

- [Homebrew Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
- [Python Formula Guidelines](https://docs.brew.sh/Python-for-Formula-Authors)
- [Main Documentation](../HOMEBREW_INSTALL.md)
- [Quick Start Guide](../QUICK_START.md)
