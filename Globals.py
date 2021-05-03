# a dictionary of image processing kernels
default_kernels = {
	"gausBlur"    : tuple([
		i/16 for i in [
			1, 2, 1, 2, 4, 2, 1, 2, 1
		]
	]),
	"sharpen"     : (
		0, -1, 0, -1, 5, -1, 0, -1, 0
	),
	"edges" : {
		0 : (
			1, 0, -1, 0, 0, 0, -1, 0, 1
		),
		1 : (
			0, -1, 0, -1, 4, -1, 0, -1, 0
		),
		2 : (
			-1, -1, -1, -1, 8, -1, -1, -1, -1
		)
	}
}