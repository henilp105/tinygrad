import numpy as np
from tqdm import trange
<<<<<<< HEAD
from tinygrad.tensor import Tensor, Device
from tinygrad.helpers import getenv, dtypes
from typing import Union
=======
from tinygrad.tensor import Tensor
from tinygrad.helpers import CI
from tinygrad.engine.jit import TinyJit
>>>>>>> master


<<<<<<< HEAD
def focal_loss(p : Tensor, y_train : Tensor, 
               alpha: float = 0.25, 
               gamma: float = 2, 
               reduction: str = "mean") -> Tensor:
    p , y_train = p.float() , y_train.float()
    p_t = p * y_train + ((Tensor.ones_like(p) - p) * (Tensor.ones_like(y_train) - y_train))
    ce_loss = -(p_t + 1e-10).log()
    loss = ce_loss.mul((Tensor.ones_like(p_t) - p_t) ** (gamma))
    if alpha >= 0:
            alpha_t = alpha * y_train + ((Tensor(1 - alpha, requires_grad=False)) * (Tensor.ones_like(y_train, requires_grad=False) - y_train))
            loss = alpha_t * loss
    if reduction == "none":
        pass
    elif reduction == "mean":
        loss = loss.mean()
    elif reduction == "sum":
        loss = loss.sum()
    return loss

def dummy_tensor_identifier(t:Tensor):
    print(" sums ", t.sum().numpy())
    print("grad info: ", t.requires_grad, t.grad)

def l1_loss(input, target, reduction: str = "none"):
    loss = (input - target).abs()
  
    if reduction == "mean":
        return loss.mean() if loss.size > 0 else 0.0 * loss.sum()
    elif reduction == "sum":
        return loss.sum()
    return loss

def smooth_l1_loss(input: Tensor, target: Tensor, 
                   beta: float, reduction: str = "none") -> Tensor:
  dti = dummy_tensor_identifier #temporal, for debugging
  if beta < 1e-5:
      return (input - target).abs()
  else:
      n = (input - target).abs()
      mask = n < beta
      #TODO this mask raises error when backwards. requires_grad=false prevents this. Loss is a function of this but this function is not differentiable.
      mask.requires_grad = False #does this cut the backward deepwalk for loss below?
      #TODO: should the .where have a requires_grad=False? where is not differentiable as well
      loss = mask.where(0.5 * (n**2) / beta, n - 0.5 * beta)

  if reduction == "mean":
      return loss.mean() if loss.numel() > 0 else 0.0 * loss.sum()
  elif reduction == "sum":
      return loss.sum()

def train(model, X_train, Y_train, optim, steps, BS=128, lossfn=sparse_categorical_crossentropy,
        transform=lambda x: x, target_transform=lambda x: x, noloss=False):
  Tensor.training = True
  losses, accuracies = [], []
  for i in (t := trange(steps, disable=getenv('CI', False))):
    samp = np.random.randint(0, X_train.shape[0], size=(BS))
    x = Tensor(transform(X_train[samp]), requires_grad=False)
    y = target_transform(Y_train[samp])
=======
def train(model, X_train, Y_train, optim, steps, BS=128, lossfn=lambda out,y: out.sparse_categorical_crossentropy(y),
        transform=lambda x: x, target_transform=lambda x: x, noloss=False, allow_jit=True):
>>>>>>> master

  def train_step(x, y):
    # network
    out = model.forward(x) if hasattr(model, 'forward') else model(x)
    loss = lossfn(out, y)
    optim.zero_grad()
    loss.backward()
    if noloss: del loss
    optim.step()
    if noloss: return (None, None)
    cat = out.argmax(axis=-1)
    accuracy = (cat == y).mean()
    return loss.realize(), accuracy.realize()

  if allow_jit: train_step = TinyJit(train_step)

  with Tensor.train():
    losses, accuracies = [], []
    for i in (t := trange(steps, disable=CI)):
      samp = np.random.randint(0, X_train.shape[0], size=(BS))
      x = Tensor(transform(X_train[samp]), requires_grad=False)
      y = Tensor(target_transform(Y_train[samp]))
      loss, accuracy = train_step(x, y)
      # printing
      if not noloss:
        loss, accuracy = loss.numpy(), accuracy.numpy()
        losses.append(loss)
        accuracies.append(accuracy)
        t.set_description("loss %.2f accuracy %.2f" % (loss, accuracy))
  return [losses, accuracies]


def evaluate(model, X_test, Y_test, num_classes=None, BS=128, return_predict=False, transform=lambda x: x,
             target_transform=lambda y: y):
  Tensor.training = False
  def numpy_eval(Y_test, num_classes):
    Y_test_preds_out = np.zeros(list(Y_test.shape)+[num_classes])
    for i in trange((len(Y_test)-1)//BS+1, disable=CI):
      x = Tensor(transform(X_test[i*BS:(i+1)*BS]))
      out = model.forward(x) if hasattr(model, 'forward') else model(x)
      Y_test_preds_out[i*BS:(i+1)*BS] = out.numpy()
    Y_test_preds = np.argmax(Y_test_preds_out, axis=-1)
    Y_test = target_transform(Y_test)
    return (Y_test == Y_test_preds).mean(), Y_test_preds

  if num_classes is None: num_classes = Y_test.max().astype(int)+1
  acc, Y_test_pred = numpy_eval(Y_test, num_classes)
  print("test set accuracy is %f" % acc)
  return (acc, Y_test_pred) if return_predict else acc

