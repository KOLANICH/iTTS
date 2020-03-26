from ipykernel.kernelapp import IPKernelApp
from .kernel import TTSKernel

__author__ = "Thomas @takluyver Kluyver"
__licese__ = "BSD-3-Clause"

def main():
	IPKernelApp.launch_instance(kernel_class=TTSKernel)


if __name__ == "__main__":
	main()
