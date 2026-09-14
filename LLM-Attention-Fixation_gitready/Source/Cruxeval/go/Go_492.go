package f_test

import (
    "testing"
    "fmt"
)

func f(text string, value string) string {
    ls := []rune(text)
    count := 0
    for i := range ls {
        if string(ls[i]) == value {
            count++
        }
    }
    if count%2 == 0 {
        for i := 0; i < len(ls); {
            if string(ls[i]) == value {
                ls = append(ls[:i], ls[i+1:]...)
            } else {
                i++
            }
        }
    } else {
        ls = nil
    }
    return string(ls)
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("abbkebaniuwurzvr", "m"), expected: "abbkebaniuwurzvr" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
