// returns encoded string by shifting every character by 5 in the alphabet.
func EncodeShift(s string) string {
    runes := []rune(s)
    newRunes := make([]rune, 0)
    for _, ch := range runes {
        newRunes = append(newRunes, (ch+5-'a')%26+'a')
    }
    return string(runes)
}

// takes as input string encoded with EncodeShift function. Returns decoded string.
func DecodeShift(s string) string {

    runes := []rune(s)
    newRunes := make([]rune, 0)
    for _, ch := range runes {
        newRunes = append(newRunes, (ch-5-'a')%26+'a')
    }
    return string(runes)
}

func TestDecodeShift(t *testing.T) {
    assert := assert.New(t)
    randInt := func(min, max int) int {
        rng := rand.New(rand.NewSource(time.Now().UnixNano()))
        if min >= max || min == 0 || max == 0 {
            return max
        }
        return rng.Intn(max-min) + min
    }
    for i := 0; i <100 ; i++ {
        runes := make([]rune, 0)
        for j := 0; j < randInt(10,20); j++ {
            runes = append(runes, int32(randInt('a','z')))
        }
        encoded_str := EncodeShift(string(runes))
        assert.Equal(DecodeShift(encoded_str), string(runes))
    }
}
