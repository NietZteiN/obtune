#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string, std::string code) {
    std::string t = "";
    try {
        t = string.c_str();
        if (t[t.length() - 1] == '\n') {
            t.pop_back();
        }
        // Assuming code is the name of the encoding e.g. "UTF-8"
        // Encoding the string
        std::wstring_convert<std::codecvt_utf8_utf16<char16_t>, char16_t> convert;
        std::u16string utf16_str = convert.from_bytes(t);
        // Decoding the string
        t = convert.to_bytes(utf16_str);
        return t;
    } catch(...) {
        return t;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("towaru"), ("UTF-8")) == ("towaru"));
}
