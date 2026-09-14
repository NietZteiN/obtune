package f_test

import (
    "testing"
    "fmt"
)

func f(cart map[int]int) map[int]int {
    for len(cart) > 5 {
        for k := range cart {
            delete(cart, k)
            break
        }
    }
    return cart
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{}), expected: map[int]int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
