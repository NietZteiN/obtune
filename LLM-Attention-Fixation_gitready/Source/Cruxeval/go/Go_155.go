package f_test

import (
    "testing"
    "fmt"
)

func f(ip string, n int) string {
    i := 0
    var out string
    for _, c := range ip {
        if i == n {
            out += "\n"
            i = 0
        }
        i++
        out += string(c)
    }
    return out
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("dskjs hjcdjnxhjicnn", 4), expected: "dskj\ns hj\ncdjn\nxhji\ncnn" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
