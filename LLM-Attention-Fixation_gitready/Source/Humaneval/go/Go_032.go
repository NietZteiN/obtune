import (
    "math"
)

// Evaluates polynomial with coefficients xs at point x.
// return xs[0] + xs[1] * x + xs[1] * x^2 + .... xs[n] * x^n
func Poly(xs []int, x float64) float64{
    sum := 0.0
    for i, coeff := range xs {
        sum += float64(coeff) * math.Pow(x,float64(i))
    }
    return sum
}
// xs are coefficients of a polynomial.
// FindZero find x such that Poly(x) = 0.
// FindZero returns only only zero point, even if there are many.
// Moreover, FindZero only takes list xs having even number of coefficients
// and largest non zero coefficient as it guarantees
// a solution.
// >>> round(FindZero([1, 2]), 2) # f(x) = 1 + 2x
// -0.5
// >>> round(FindZero([-6, 11, -6, 1]), 2) # (x - 1) * (x - 2) * (x - 3) = -6 + 11x - 6x^2 + x^3
// 1.0
func FindZero(xs []int) float64 {

    begin := -1.0
	end := 1.0
	for Poly(xs, begin)*Poly(xs, end) > 0 {
		begin *= 2
		end *= 2
	}
	for end-begin > 1e-10 {
		center := (begin + end) / 2
		if Poly(xs, center)*Poly(xs, begin) > 0 {
			begin = center
		} else {
			end = center
		}
	}
	return begin
}

func TestFindZero(t *testing.T) {
    assert := assert.New(t)
    randInt := func(min, max int) int {
        rng := rand.New(rand.NewSource(42))
        if min >= max || min == 0 || max == 0 {
            return max
        }
        return rng.Intn(max-min) + min
    }
    copyInts := func(src []int) []int {
        ints := make([]int, 0)
        for _, i := range src {
            ints = append(ints, i)
        }
        return ints
    }
    for i := 0; i < 100; i++ {
        ncoeff := 2 * randInt(1, 4)
        coeffs := make([]int, 0)
        for j := 0; j < ncoeff; j++ {
            coeff := randInt(-10, 10)
            if coeff == 0 {
                coeff = 1
            }
            coeffs = append(coeffs, coeff)
        }
        solution := FindZero(copyInts(coeffs))
        assert.Equal(true, math.Abs(Poly(coeffs,solution))<1e-4)
    }
}
