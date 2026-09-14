package f_test

import (
    "testing"
    "fmt"
)

func f(d map[int]int, index int) int {
    length := len(d)
    idx := index % length
    for i := 0; i < idx; i++ {
        for k := range d {
            delete(d, k)
            break
        }
    }
    var v int
    for _, value := range d {
        v = value
        break
    }
    return v
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{27: 39}, 1), expected: 39 },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
