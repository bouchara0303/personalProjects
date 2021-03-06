# QR Code Generator

This application is used to generate version 4 QR codes with error correction level M. Currently it only supports alphanumeric encoding as well as byte encoding. Eventually I will include support for different QR versions and character modes.

## Getting Started

Keep all files in same directory. If you would like to add an image to the QR Code, you must add an image in the same directory as well.

Make sure to include the QR class like so:
```python
from QR import QR
```

To generate a QR code simply supply the generate function with its necessary parameters. Use B for byte encoding and A for alphanumeric encoding:
```python
QR().generate('b', 'hello, world!', 'y', 'github.png', '492E6B')
```

### Prerequisites

You need to have both the PIL and numpy libraries installed.

Note: Pillow cannot coexist with the PIL library. If you have PIL installed then uninstall using:
```
pip3 uninstall PIL
```

Then:
```
pip3 install numpy Pillow
```

## Built With

* [Pillow](https://python-pillow.org) - Image processing used
* [NumPy](http://www.numpy.org) - Python array manipulation
* [reedSolomon.py](https://rextester.com/ZMBYT68318) - Used to generate error correction modules -- (Unknown author)


## Authors

* **Austin Bouchard**


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks to the author of [reedSolomon.py](QRGenerator/reedSolomon.py) for making the encoding process easier!
