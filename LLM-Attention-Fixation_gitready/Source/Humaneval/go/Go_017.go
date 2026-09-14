
// Input to this function is a string representing musical notes in a special ASCII format.
// Your task is to parse this string and return list of integers corresponding to how many beats does each
// not last.
// 
// Here is a legend:
// 'o' - whole note, lasts four beats
// 'o|' - half note, lasts two beats
// '.|' - quater note, lasts one beat
// 
// >>> ParseMusic('o o| .| o| o| .| .| .| .| o o')
// [4, 2, 1, 2, 2, 1, 1, 1, 1, 4, 4]
func ParseMusic(music_string string) []int{

    note_map := map[string]int{"o": 4, "o|": 2, ".|": 1}
	split := strings.Split(music_string, " ")
	result := make([]int, 0)
	for _, x := range split {
		if i, ok := note_map[x]; ok {
			result = append(result, i)
		}
	}
	return result
}

func TestParseMusic(t *testing.T) {
    assert := assert.New(t)
    assert.Equal([]int{}, ParseMusic(""))
    assert.Equal([]int{4, 4, 4, 4}, ParseMusic("o o o o"))
    assert.Equal([]int{1, 1, 1, 1}, ParseMusic(".| .| .| .|"))
    assert.Equal([]int{2, 2, 1, 1, 4, 4, 4, 4}, ParseMusic("o| o| .| .| o o o o"))
    assert.Equal([]int{2, 1, 2, 1, 4, 2, 4, 2}, ParseMusic("o| .| o| .| o o| o o|"))
}
