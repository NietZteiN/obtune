import (
    "strings"
)

// Given a string s, count the number of uppercase vowels in even indices.
// 
// For example:
// CountUpper('aBCdEf') returns 1
// CountUpper('abcdefg') returns 0
// CountUpper('dBBE') returns 0
func CountUpper(s string) int {

    count := 0
    runes := []rune(s)
    for i := 0; i < len(runes); i += 2 {
        if strings.ContainsRune("AEIOU", runes[i]) {
            count += 1
        }
    }
    return count
}

func TestCountUpper(t *testing.T) {
    assert := assert.New(t)
    assert.Equal(1, CountUpper("aBCdEf"))
    assert.Equal(0, CountUpper("abcdefg"))
    assert.Equal(0, CountUpper("dBBE"))
    assert.Equal(0, CountUpper("B"))
    assert.Equal(1, CountUpper("U"))
    assert.Equal(0, CountUpper(""))
    assert.Equal(2, CountUpper("EEEE"))
}
