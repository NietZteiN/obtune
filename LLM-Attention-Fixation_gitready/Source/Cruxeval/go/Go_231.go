package f_test

import (
    "testing"
    "fmt"
)

func f(years []int) int {
    a10 := 0
    a90 := 0
    for _, x := range years {
        if x <= 1900 {
            a10++
        } else if x > 1910 {
            a90++
        }
    }

    if a10 > 3 {
        return 3
    } else if a90 > 3 {
        return 1
    } else {
        return 2
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]int{1872, 1995, 1945}), expected: 2 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
