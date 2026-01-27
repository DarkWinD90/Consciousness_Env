class ConsciousnessEnv < Formula
  include Language::Python::Virtualenv

  desc "Multi-Layer Architecture for Synthetic Proto-Consciousness"
  homepage "https://github.com/DarkWinD90/Consciousness_Env"
  # Note: Replace URL and SHA256 with actual release values when creating a release
  # For development, install from the repository directly
  head "https://github.com/DarkWinD90/Consciousness_Env.git", branch: "main"

  depends_on "python@3.11"

  # Python dependencies from requirements.txt
  resource "numpy" do
    url "https://files.pythonhosted.org/packages/source/n/numpy/numpy-1.26.0.tar.gz"
    sha256 "f93fc78fe8b7c8c6e9c4bc5e9bb46f0e20a6fb0a8e8e2f4f6e8e0e0e0e0e0e0e"
  end

  resource "matplotlib" do
    url "https://files.pythonhosted.org/packages/source/m/matplotlib/matplotlib-3.8.0.tar.gz"
    sha256 "df8505e1c19d5c2c26aff3497a7cbd3ccfc2e97043d1e4db3e76afa399164b69"
  end

  resource "networkx" do
    url "https://files.pythonhosted.org/packages/source/n/networkx/networkx-3.2.1.tar.gz"
    sha256 "9f1bb5cf3409bf324e0a722c20bdb4c20ee39bf1c30ce8ae319e955b0e4e4f40"
  end

  resource "scipy" do
    url "https://files.pythonhosted.org/packages/source/s/scipy/scipy-1.11.3.tar.gz"
    sha256 "bba4d955f54edd61899776bad459bf7326e14b9fa1c552181f0479cc60a568cd"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"consciousness", "version"
  end
end
