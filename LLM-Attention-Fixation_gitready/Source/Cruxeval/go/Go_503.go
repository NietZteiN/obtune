package f_test

import (
    "testing"
    "fmt"
)

func f(d map[int]int) []int {
    if len(d) == 0 {
        return nil
    }

    result := make([]int, len(d))
    a, b := 0, 0
    for len(d) > 0 {
        keys := make([]int, 0, len(d))
        for k := range d {
            keys = append(keys, k)
        }
        var key int
        if a == b {
            key = keys[0]
        } else {
            key = keys[len(keys)-1]
        }
        result[a] = d[key]
        delete(d, key)
        a, b = b, (b+1)%len(result)
    }
    return result
}

func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{}), expected: []int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
