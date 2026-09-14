package f_test

import (
	"testing"
	"fmt"
)

func f(array map[int]int, elem int) map[int]int {
	result := make(map[int]int)
	for k, v := range array {
		result[k] = v
	}

	for len(result) > 0 {
		for key, value := range result {
			if key == elem || value == elem {
				for k, v := range array {
					result[k] = v
				}
			}
			delete(result, key)
			break
		}
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
     { actual: candidate(map[int]int{}, 1), expected: map[int]int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
