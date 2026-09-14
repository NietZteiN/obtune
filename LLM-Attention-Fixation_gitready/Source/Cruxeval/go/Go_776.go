package f_test

import (
    "testing"
    "fmt"
)

func f(dictionary map[int]int) map[string]int {
    a := make(map[string]int)
    for key, value := range dictionary {
        if key % 2 != 0 {
            continue
        }
        a[fmt.Sprintf("$%d", key)] = value
    }
    return a
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[int]int{}), expected: map[string]int{} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
