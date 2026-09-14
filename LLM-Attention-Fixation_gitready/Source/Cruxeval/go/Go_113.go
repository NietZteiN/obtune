package f_test

import (
    "fmt"
    "testing"
)

func f(line string) string {
    count := 0
    var a []rune
    for _, v := range line {
        count++
        if count%2 == 0 {
            a = append(a, swapCase(v))
        } else {
            a = append(a, v)
        }
    }
    return string(a)
}

func swapCase(r rune) rune {
    if r >= 'a' && r <= 'z' {
        return r - 32
    } else if r >= 'A' && r <= 'Z' {
        return r + 32
    }
    return r
}
func TestF(t *testing.T) {
  candidate := f
	type test struct {
		actual   interface{}
		expected interface{}
	}
   tests := []test{
     { actual: candidate("987yhNSHAshd 93275yrgSgbgSshfbsfB"), expected: "987YhnShAShD 93275yRgsgBgssHfBsFB" },
   }

	for i, tc := range tests {
		t.Run(fmt.Sprintf("test num % d", i), func(t *testing.T) {
			if fmt.Sprintf("%v", tc.actual) != fmt.Sprintf("%v", tc.expected) {
				t.Errorf("expected '%s', got '%s'", tc.expected, tc.actual)
			}
		})
	}
}
