package f_test

import (
    "testing"
    "fmt"
)

func f(d map[int]int, count int) map[int]int {
    for i := 0; i < count; i++ {
        if len(d) == 0 {
            break
        }
        for k := range d {
            delete(d, k)
            break
        }
    }
    return d
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{}, 200), expected: map[int]int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
