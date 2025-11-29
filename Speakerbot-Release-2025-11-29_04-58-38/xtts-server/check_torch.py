import importlib, sys

spec = importlib.util.find_spec('torch')
if not spec:
    print('NOT_INSTALLED: torch not found')
    sys.exit(0)

import torch
import torchaudio

print('TORCH_VERSION:', torch.__version__)
print('TORCH_CUDA_AVAILABLE:', torch.cuda.is_available())
print('TORCH_CUDA_VERSION:', getattr(torch, 'version', None) and torch.version.cuda)
print('TORCHAUDIO_VERSION:', getattr(torchaudio, '__version__', 'n/a'))

# Print device allocation information
try:
    print('CUDA_DEVICES:', torch.cuda.device_count())
    if torch.cuda.is_available():
        print('CUDA_DEVICE_NAME:', torch.cuda.get_device_name(0))
except Exception as e:
    print('CUDA_INFO_ERROR:', e)
