package f_test

import (
    "testing"
    "fmt"
)

func f(text string) string {
    count := 0
    for i := range text {
        if text[i] == text[0] {
            count++
        } else {
            break
        }
    }

    ls := []byte(text)
    for i := 0; i < count; i++ {
        ls = append(ls[:0], ls[1:]...)
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
     { actual: candidate(";,,,?"), expected: ",,,?" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
