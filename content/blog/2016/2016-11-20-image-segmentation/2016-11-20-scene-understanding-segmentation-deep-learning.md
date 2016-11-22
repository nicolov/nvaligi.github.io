Date: 2016-11-20
Slug: converting-deep-learning-model-caffe-keras
Summary: Converting a Deep learning model from Caffe to Keras
Title: Converting a Deep learning model from Caffe to Keras
Tags: deep learning, keras

<img src="{attach}cat.jpg"
     class="img-center"
     alt="Segmenting cat images with Deep Learning"
     style="max-width: 600px"/>

A lot of Deep Learning researchers use the [Caffe framework](http://caffe.berkeleyvision.org/) to develop new networks and models. I suspect this is at least partly because of the many pre-trained models available in its [Model Zoo](https://github.com/albertomontesg/keras-model-zoo). Using pre-trained weights has several advantages:

- there's never enough training data around. Niche applications really benefit from pretraining on ImageNet-sized datasets,
- training from scratch is slow, expensive, and tricky

However, I really can't get behind Caffe's heavy use of protobufs for network definition ([code *is* data](http://stackoverflow.com/questions/5833033/in-lisp-code-is-data-what-benefit-does-that-provide), after all). This lack of flexibility forces everybody to fork the codebase for minor details, like image preprocessing. And you get to write that in C++, of all things.

I much prefer the approach of TensorFlow and friends, where the computational graph can be built up using the full power of Python functions. This flexibility extends to the pre-processing steps, that are much more reusable when written in a scripting language, outside of the framework code. I usually enjoy working with Keras, since it makes the easy things easy, and the hard things possible (TM).

In this post I will go through the process of converting a pre-trained Caffe network to a Keras model that can be used for inference and fine tuning on different datasets. You can see the end result here: [Keras DilatedNet](https://github.com/nicolov/segmentation_keras). I will assume knowledge of Python and Keras.

## Picking a model for image segmentation

Lately, I've been researching the state of the art in image segmentation, and came up with a few potential models that I wanted to understand and work on:

- [SegNet](http://mi.eng.cam.ac.uk/projects/segnet/) uses a standard Encoder-Decoder network, and also has an interesting Bayesian extension. Pretrained weights on CamVid.
- [DilatedNet](https://github.com/fyu/dilation) does away with the autoencoder structure by adopting *dilated* convolutions that are provably better for pixel-wise labeling.
- [Fully Convolutional Networks for Semantic Segmentation](https://arxiv.org/pdf/1411.4038.pdf) resembles a classification network, with a single fully-connected layer for the output.

I ended up starting my exploration with the second, since it seems to perform better thanks to *dilated convolutions*, and comes with very clean Caffe code.

## Converting the weights

Caffe stores weights in `*.caffemodel` files, which are just serialized Protocol Buffers. We're going to use [caffe-tensorflow](https://github.com/ethereon/caffe-tensorflow) to convert these to an HD5 file that can easily be loaded into numpy. The script will convert the `.prototxt` (network definition) and `.caffemodel` files to produce weights and a TensorFlow graph.

```
:::bash
python convert.py \
  --caffemodel=~/dilation/pretrained/dilation8_pascal_voc.caffemodel \
  --code-output-path=./pascal_voc_tf/dil8_net.py \
  --data-output-path=./pascal_voc_tf/ \
  ~/dilation/models/dilation8_pascal_voc_deploy.prototxt
```

The weights convert fine, but the network doesn't (it's missing a few important details, and won't work as-is). We're going to do it manually for Keras anyways.

## Converting the network definition

This step is just going to be a rote transcription of the network definition, layer by layer. I've used the [Keras example](https://gist.github.com/fchollet/f35fbc80e066a49d65f1688a7e99f069) for VGG16 and the corresponding [Caffe definition]() to get the hang of the process.

For example, this Caffe `.prototxt`:

    :::protobuf
    layer {
      name: "conv1_2"
      type: "Convolution"
      bottom: "conv1_1"
      top: "conv1_2"
      convolution_param {
        num_output: 64
        kernel_size: 3
      }
    }
    layer {
      name: "relu1_2"
      type: "ReLU"
      bottom: "conv1_2"
      top: "conv1_2"
    }

converts to the equivalent Keras:

    :::python
    model.add(Convolution2D(64, 3, 3, activation='relu', name='conv1_2'))

There's a few things to keep in mind:

- Keras/Tensorflow stores images in order *(rows, columns, channels)*, whereas Caffe uses *(channels, rows, columns)*. `caffe-tensorflow` automatically fixes the weights, but any preprocessing steps need to as well,
- padding is another tricky detail: you can dump the activation of the intermediate layers to make sure that the shapes match at each step

Now that the definition is complete, we add some code to load the weights from the HD5 file. By doing it layer-by-layer, new layers can be added at the top without issues:

    :::python
    weights_data = np.load(weights_path).item()
    model = get_model()

    for layer in model.layers:
        if layer.name in weights_data.keys():
            layer_weights = weights_data[layer.name]

            layer.set_weights((layer_weights['weights'],
                layer_weights['biases']))


You don't need to worry about mis-matched shapes, as Keras will throw errors in that case.

## Tips and tricks

Like any classification problem, semantic segmentation needs a Softmax layer at the top to produce normalized probabilities. In this case, we need *pixel-wise* softmax, as the network must produce a label for each of the pixels in the image. Since Keras' softmax layer doesn't work on 4D arrays, the pixel data must be reshaped to a 1D vector beforehand. Softmax is applied across the last axis (*channels*), so its shape (usually) corresponds to the number of classes in the classification. The following code does this:

    :::python
    curr_width, curr_height, curr_channels = model.layers[-1].output_shape[1:]
    model.add(Reshape((curr_width*curr_height, curr_channels)))
    model.add(Activation('softmax'))
    model.add(Reshape((curr_width, curr_height, curr_channels)))

While troubleshooting, it's useful to check the activations at middle layers in the network. As we're only working on the forward pass, we can cut off a part of the Keras `Sequential` model to look at middle layers. For Caffe's Python wrapper, we can look at the `blobs` property of the `Net` object:

    :::python
    np.save(layer_name, net.blobs[layer_name].data)

## Next up: training

I've uploaded the complete code on [my Github](https://github.com/nicolov/segmentation_keras), where you can check the results using a few of the sample images from the original paper. Now that the inference works, the next step is setting up the training infrastructure to fine-tune the pretrained network on different datasets.