package f_test

import (
    "testing"
    "fmt"
)

func f(row string) []interface{} {
    count_one := 0
    count_zero := 0
    for _, v := range row {
        if v == '1' {
            count_one += 1
        } else if v == '0' {
            count_zero += 1
        }
    }
    return []interface{}{count_one, count_zero}
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("100010010"), expected: []interface{}{3, 6} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
