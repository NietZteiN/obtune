package f_test

import (
    "testing"
    "fmt"
)

func f(text string) map[string]int {
    dic := make(map[string]int)
    for _, char := range text {
        strChar := string(char)
        dic[strChar] = dic[strChar] + 1
    }
    for key, value := range dic {
        if value > 1 {
            dic[key] = 1
        }
    }
    return dic
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("a"), expected: map[string]int{"a": 1} },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
