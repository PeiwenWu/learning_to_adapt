from keras.models import Model, Sequential, load_model
from keras.layers import Activation, Dense, Conv1D, Input
import keras.backend as K
import numpy as np
import unittest

from learning_to_adapt.model.layers import FeatureTransform, LHUC
from learning_to_adapt.model.wrapper import create_model_wrapper, get_model_weights, set_model_weights


class TestWrapper(unittest.TestCase):

  def testForwardPass(self):
    batch_size = 10
    model = self.build_model()
    wrapper = self.build_wrapped_model(model)

    params = np.array([[1., 1., 0., 0., 1., 2., 3., 4., 5., 6., 1., 1.]])
    x = np.array([[[1., 2.]] * batch_size])
    expected_result = np.array([[[12., 16.]] * batch_size])

    prediction = wrapper.predict([params, params, x])
    np.testing.assert_allclose(expected_result, prediction)

  def testBatchForwardPass(self):
    batch_size = 1
    model = self.build_convolutional_model()
    wrapper = self.build_wrapped_model(model, batch_size=2)

    params = np.array([
        [1., 2., 3., 4., 5., 6., 1., 1.],
        [0., 0., 0., 0., 0., 0., 0., 0.],
    ])
    x = np.expand_dims(np.array([
        [[1., 2.]] * batch_size,
        [[1., 1.]] * batch_size
    ]), 1)
    expected_result = np.expand_dims(np.array([
        [[12., 16.]] * batch_size,
        [[0., 0.]] * batch_size
    ]), 1)

    prediction = wrapper.predict([params, params, x])
    np.testing.assert_allclose(expected_result, prediction)

  def testForwardPassWithTrainableWeights(self):
    batch_size = 10
    model = self.build_model()
    for l in model.layers:
      l.trainable = l.name.startswith("dense")

    wrapper = self.build_wrapped_model(model)

    params = np.array([[1., 1., 0., 0., 1., 0., 0., 1., -1., -1., 1., 1.]])
    trainable_params = np.array([[1., 2., 3., 4., 5., 6.]])
    x = np.array([[[1., 2.]] * batch_size])
    expected_result = np.array([[[12., 16.]] * batch_size])

    prediction = wrapper.predict([params, trainable_params, x])
    np.testing.assert_allclose(expected_result, prediction)

  def testForwardPassWithConvolutionalLayers(self):
    batch_size = 10
    model = self.build_convolutional_model()
    wrapper = self.build_wrapped_model(model)

    params = np.array([[1., 2., 3., 4., 5., 6., 1., 1.]])
    x = np.expand_dims(np.array([[[1., 2.]] * batch_size]), 1)
    expected_result = np.expand_dims(np.array([[[12., 16.]] * batch_size]), 1)

    prediction = wrapper.predict([params, params, x])
    np.testing.assert_allclose(expected_result, prediction)

  def testGetAllWeights(self):
    model = self.build_model()
    model.set_weights((np.ones(2), np.zeros(2), np.eye(2), np.zeros(2), np.ones(2)))
    wrapper = create_model_wrapper(model)

    expected_weights = np.array([1., 1., 0., 0., 1., 0., 0., 1., 0., 0., 1., 1.])
    np.testing.assert_allclose(expected_weights, get_model_weights(model))

  def testGetParamGroups(self):
    model = self.build_model()
    wrapper = create_model_wrapper(model)

    expected_groups = [(0, 4), (4, 10), (10, 12)]
    self.assertEqual(expected_groups, list(wrapper.param_groups()))

  def testGetParamGroupsWithTrainableParameters(self):
    model = self.build_model()
    for l in model.layers:
      l.trainable = l.name.startswith("dense")
    wrapper = create_model_wrapper(model)

    expected_groups = [(0, 6)]
    self.assertEqual(expected_groups, list(wrapper.param_groups()))

  def build_wrapped_model(self, model, batch_size=1):
    wrapper = create_model_wrapper(model, batch_size=batch_size)
    params = Input(shape=(wrapper.num_params,))
    trainable_params = Input(shape=(wrapper.num_trainable_params,))
    x = Input(shape=K.int_shape(model.inputs[0]))
    y = wrapper([params, trainable_params, x])

    return Model(inputs=[params, trainable_params, x], outputs=[y])

  def build_model(self):
    model = Sequential()
    model.add(FeatureTransform(input_shape=(2,)))
    model.add(Dense(2))
    model.add(Activation('relu'))
    model.add(LHUC())
    model.compile(loss='mse', optimizer='SGD')

    return model

  def build_convolutional_model(self):
    model = Sequential()
    model.add(Conv1D(2, 1, activation='relu', use_bias=True, input_shape=(None, 2)))
    model.add(LHUC())
    model.compile(loss='mse', optimizer='SGD')

    return model
