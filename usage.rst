Usage
=====

This guide demonstrates how to use the Hashtron Network Implementation.

Installation
------------

Install the package using pip:

.. code-block:: bash

   pip install hashtron

Basic Usage
-----------

1. Import the necessary modules:

   .. code-block:: python

      from hashtron.net.feedforward.net import Net
      from hashtron.layer.majpool2d.layer import MajPool2DLayer
      from hashtron.datasets.mnist.mnist import MNISTDataset
      import urllib.request
      import tempfile
      import os

2. Create and configure the network:

   .. code-block:: python

      # Specify network size
      fanout1 = 3
      fanout2 = 5
      fanout3 = 3
      fanout4 = 5

      # Create a Hashtron network
      tron = Net.new()
      tron.new_layer(fanout1 * fanout2 * fanout3 * fanout4, 0, 1 << fanout4)
      tron.new_combiner(MajPool2DLayer(fanout1 * fanout2 * fanout4, 1, fanout3, 1, fanout4, 1, 1))
      tron.new_layer(fanout1 * fanout2, 0, 1 << fanout2)
      tron.new_combiner(MajPool2DLayer(fanout2, 1, fanout1, 1, fanout2, 1, 1))
      tron.new_layer(1, 0)

3. Load the model weights:

   .. code-block:: python

      filename = os.path.expanduser('~/classifier/cmd/train_mnist/output.77.json.t.zlib')
      if os.path.exists(filename):
          ok = tron.io.read_zlib_weights_from_file(filename)
      else:
          # Load online model weights
          with urllib.request.urlopen('https://www.hashtron.cloud/dl/mnist/output.77.json.t.zlib') as f:
              with tempfile.NamedTemporaryFile(delete=True) as dst_file:
                  data = f.read()
                  dst_file.write(data)
                  ok = tron.io.read_zlib_weights_from_file(dst_file.name)

      if not ok:
          raise Exception('Model weights were not loaded')

4. Test the network on the MNIST dataset:

   .. code-block:: python

      for i in range(2):
          # Load offline or online MNIST dataset
          try:
              dataset = MNISTDataset(True, i == 0)
          except FileNotFoundError:
              dataset = MNISTDataset(True, i == 0, MNISTDataset.download())

          correct = 0
          for sample in dataset:
              pred = tron.network.infer(sample) & 1
              actual = sample.output() & 1
              if pred == actual:
                  correct += 1
          print(100 * correct // len(dataset), '% on', len(dataset), 'MNIST samples')

Contributing
------------

To contribute to this project:

1. Open an issue.
2. Fork the repository.
3. Implement the required changes (avoid adding large files to the repository; host datasets or demo models externally).
4. Add tests as needed.
5. Install the package in development mode:

   .. code-block:: bash

      pip install -e .

6. Run all test cases:

   .. code-block:: bash

      pip install pytest
      python3 -m pytest

7. Submit a pull request.

License
-------

This project is licensed under the MIT License. See the `LICENSE` file for details.

