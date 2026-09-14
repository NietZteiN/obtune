package f_test

import (
    "testing"
    "fmt"
)

func f(d map[string]int, l []string) map[string]int {
    new_d := make(map[string]int)

    for _, k := range l {
        if val, ok := d[k]; ok {
            new_d[k] = val
        }
    }

    return new_d
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate(map[string]int{"lorem ipsum": 12, "dolor": 23}, []string{"lorem ipsum", "dolor"}), expected: map[string]int{"lorem ipsum": 12, "dolor": 23} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
