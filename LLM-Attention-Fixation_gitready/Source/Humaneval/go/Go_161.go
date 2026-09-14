
// You are given a string s.
// if s[i] is a letter, reverse its case from lower to upper or vise versa,
// otherwise keep it as it is.
// If the string contains no letters, reverse the string.
// The function should return the resulted string.
// Examples
// Solve("1234") = "4321"
// Solve("ab") = "AB"
// Solve("#a@C") = "#A@c"
func Solve(s string) string {

    flg := 0
    new_str := []rune(s)
    for i, r := range new_str {
        if ('a' <= r && r <= 'z') || ('A' <= r && r <= 'Z') {
            if 'a' <= r && r <= 'z' {
                new_str[i] = r - 'a' + 'A'
            } else {
                new_str[i] = r - 'A' + 'a'
            }
            flg = 1
        }
    }
    if flg == 0 {
        for i := 0;i < len(new_str)>>1;i++ {
            new_str[i], new_str[len(new_str)-i-1] = new_str[len(new_str)-i-1], new_str[i]
        }
    }
    return string(new_str)
}

func TestSolve(t *testing.T) {
    assert := assert.New(t)
    assert.Equal("aSdF", Solve("AsDf"))
    assert.Equal("4321", Solve("1234"))
    assert.Equal("AB", Solve("ab"))
    assert.Equal("#A@c", Solve("#a@C"))
    assert.Equal("#aSDFw^45", Solve("#AsdfW^45"))
    assert.Equal("2@6#", Solve("#6@2"))
    assert.Equal("#$A^d", Solve("#$a^D"))
    assert.Equal("#CCC", Solve("#ccc"))
}
