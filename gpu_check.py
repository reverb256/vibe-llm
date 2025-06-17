import torch

def main():
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("CUDA device count:", torch.cuda.device_count())
        print("CUDA device name:", torch.cuda.get_device_name(0))
    else:
        print("No CUDA devices found.")

if __name__ == "__main__":
    main()
