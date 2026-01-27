class ConsciousnessEnv < Formula
  include Language::Python::Virtualenv

  desc "Multi-Layer Architecture for Synthetic Proto-Consciousness"
  homepage "https://github.com/DarkWinD90/Consciousness_Env"
  # Install from HEAD (development version)
  # For stable releases, replace with:
  # url "https://github.com/DarkWinD90/Consciousness_Env/archive/refs/tags/v1.0.0.tar.gz"
  # sha256 "calculated_sha256_of_release_tarball"
  head "https://github.com/DarkWinD90/Consciousness_Env.git", branch: "main"

  depends_on "python@3.11"

  def install
    # Install the package and all its dependencies using virtualenv
    # This automatically handles all dependencies from requirements.txt
    virtualenv_install_with_resources
  end

  test do
    # Test that the CLI tool was installed and works
    system bin/"consciousness", "version"
  end
end
