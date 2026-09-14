#include<assert.h>
#include<bits/stdc++.h>
#include<locale>
#include<codecvt>

bool is_unicode_whitespace(char32_t c) {
    return std::isspace(c) || c == 0x3000;
}

bool f(std::string text) {
    std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> converter;
    std::u32string u32text = converter.from_bytes(text);
    return std::all_of(u32text.begin(), u32text.end(), is_unicode_whitespace);
}
int main() {
    auto candidate = f;
    assert(candidate((" 	  　")) == (true));
}
