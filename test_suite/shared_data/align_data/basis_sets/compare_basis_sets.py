# Random tensors of {Axx, Ayy, Axy, Axz, Ayz} generated using random.uniform(0, 1e-4).
tensor1 = [5.4839183673166663e-05, 3.692459844061351e-05, 1.994164790083226e-05, 4.5945264935308495e-05, 1.0090119622465559e-05]
tensor2 = [1.5832157768761617e-05, -4.9797877146095514e-05, -3.6007226809999e-05, -3.8175058915299295e-05, 5.3131759988544946e-05]
tensor3 = [3.892445496049645e-05, -1.7165585393754253e-05, 7.803231512226243e-05, -3.057296854986567e-05, 9.31348723610886e-05]
tensor4 = [4.6720247808382186e-05, -9.140580842599e-05, -3.415945182796103e-05, -1.7753928806205142e-05, 5.20457038882803e-05]

# Create a N-state analysis data pipe.
pipe.create('basis set comparison', 'N-state')

# Load the tensors.
align_tensor.init(tensor='t1', align_id='t1', params=tuple(tensor1))
align_tensor.init(tensor='t2', align_id='t2', params=tuple(tensor2))
align_tensor.init(tensor='t3', align_id='t3', params=tuple(tensor3))
align_tensor.init(tensor='t4', align_id='t4', params=tuple(tensor4))

# Display.
align_tensor.display()

# Inter-tensor angles.
align_tensor.matrix_angles(basis_set='matrix')
align_tensor.matrix_angles(basis_set='irreducible 5D')
align_tensor.matrix_angles(basis_set='unitary 9D')
align_tensor.matrix_angles(basis_set='unitary 5D')
align_tensor.matrix_angles(basis_set='geometric 5D')

# SVD.
align_tensor.svd(basis_set='irreducible 5D')
align_tensor.svd(basis_set='unitary 9D')
align_tensor.svd(basis_set='unitary 5D')
align_tensor.svd(basis_set='geometric 5D')
