package f_test

import (
    "testing"
    "fmt"
)

func f(fruits []string) []string {
    if fruits[len(fruits)-1] == fruits[0] {
        return []string{"no"}
    } else {
        fruits = fruits[2 : len(fruits)-2]
        return fruits
    }
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"apple", "apple", "pear", "banana", "pear", "orange", "orange"}), expected: []string{"pear", "banana", "pear"} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
