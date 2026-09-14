package f_test

import (
    "testing"
    "fmt"
)

func f(a string) string {
    for i := 0; i < 10; i++ {
        for j := 0; j < len(a); j++ {
            if a[j] != '#' {
                a = a[j:]
                break
            }
        }
        if len(a) == 0 {
            break
        }
    }
    for len(a) > 0 && a[len(a)-1] == '#' {
        a = a[:len(a)-1]
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
     { actual: candidate("##fiu##nk#he###wumun##"), expected: "fiu##nk#he###wumun" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
