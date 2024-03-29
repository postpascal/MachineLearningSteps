import numpy as np
class RNN():
	def __init__(self, u, v, w):
		self._u, self._v, self._w = np.asarray(u), np.asarray(v), np.asarray(w)
		self._states = None

	def activate(self, x):
		return 1 / (1 + np.exp(-x))

	def run(self, x):
		output = []
		x = np.atleast_2d(x)
		# 初始化 States 矩阵为零矩阵
		# 之所以把所有 States 记下来、是因为训练时（BPTT 算法）要用到
		self._states = np.zeros([len(x)+1, self._u.shape[0]])
		for t, xt in enumerate(x):

			self._states[t] = self.activate(
				self._u.dot(xt) + self._w.dot(self._states[t-1])
			)
			output.append(self.transform(
				self._v.dot(self._states[t]))
			)
		return np.array(output)


	def transform(self, x):
		safe_exp = np.exp(x - np.max(x))
		return safe_exp / np.sum(safe_exp)

	def bptt(self, x, y):
		x, y, n = np.asarray(x), np.asarray(y), len(y)
		o = self.run(x)

		dis = o - y
		dv = dis.T.dot(self._states[:-1])
		du = np.zeros_like(self._u)
		dw = np.zeros_like(self._w)
		for t in range(n-1, -1, -1):
			st = self._states[t]
			ds = self._v.T.dot(dis[t]) * st * (1 - st)
			# 这里额外设定了最多往回看 10 步
			for bptt_step in range(t, max(-1, t-10), -1):
				du += np.outer(ds, x[bptt_step])
				dw += np.outer(ds, self._states[bptt_step-1])
				st = self._states[bptt_step-1]
				ds = self._w.T.dot(ds) * st * (1 - st)
		return du, dv, dw

	def loss(self, x, y):
		o = self.run(x)
		return np.sum(
			-y * np.log(np.maximum(o, 1e-12)) -
			(1 - y) * np.log(np.maximum(1 - o, 1e-12))
		)