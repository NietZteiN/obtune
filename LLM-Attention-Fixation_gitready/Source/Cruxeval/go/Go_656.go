package f_test

import (
    "testing"
    "fmt"
)

func f(letters []string) string {
    a := make([]string, 0)
    for i := 0; i < len(letters); i++ {
        for _, char := range a {
            if char == letters[i] {
                return "no"
            }
        }
        a = append(a, letters[i])
    }
    return "yes"
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate([]string{"b", "i", "r", "o", "s", "j", "v", "p"}), expected: "yes" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
