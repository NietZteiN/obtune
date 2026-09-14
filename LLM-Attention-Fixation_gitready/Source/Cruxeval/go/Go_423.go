package f_test

import (
    "testing"
    "fmt"
)

func f(selfie []int) []int {
    lo := len(selfie)
    for i := lo - 1; i >= 0; i-- {
        if selfie[i] == selfie[0] {
            selfie = append(selfie[:lo-1], selfie[lo:]...)
            break
        }
    }
    return selfie
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{4, 2, 5, 1, 3, 2, 6}), expected: []int{4, 2, 5, 1, 3, 2} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
