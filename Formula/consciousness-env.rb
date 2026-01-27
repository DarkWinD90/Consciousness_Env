class ConsciousnessEnv < Formula
  include Language::Python::Virtualenv

  desc "Multi-Layer Architecture for Synthetic Proto-Consciousness"
  homepage "https://github.com/DarkWinD90/Consciousness_Env"
  url "https://github.com/DarkWinD90/Consciousness_Env/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "TBD"

  depends_on "python@3.11"

  resource "matplotlib" do
    url "https://files.pythonhosted.org/packages/matplotlib/matplotlib-3.8.0.tar.gz"
    sha256 "df8505e1c19d5c2c26aff3497a7cbd3ccfc2e97043d1e4db3e76afa399164b69"
  end

  resource "networkx" do
    url "https://files.pythonhosted.org/packages/networkx/networkx-3.2.1.tar.gz"
    sha256 "9f1bb5cf3409bf324e0a722c20bdb4c20ee39bf1c30ce8ae319e955b0e4e4f4"
  end

  resource "numpy" do
    url "https://files.pythonhosted.org/packages/numpy/numpy-1.26.0.tar.gz"
    sha256 "f93fc78fe8b7c8c6e9c9f5c7e4f7eeb5c7d9c9d9e9e9e9f9e9e9f9e9f9f9e9e9"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"consciousness", "version"
  end
end
