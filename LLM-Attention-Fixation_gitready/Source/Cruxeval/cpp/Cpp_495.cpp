#include<assert.h>
#include<bits/stdc++.h>
std::tuple<std::string, std::string> f(std::string s) {
    std::string last5 = s.substr(s.length() - 5);
    std::string first3 = s.substr(0, 3);
    std::string first5 = s.substr(0, 5);
    std::string last3 = s.substr(s.length() - 3);

    bool last5Ascii = std::all_of(last5.begin(), last5.end(), ::isascii);
    bool first5Ascii = std::all_of(first5.begin(), first5.end(), ::isascii);
    if (last5Ascii) {
        return std::make_tuple(last5, first3);
    } else if (first5Ascii) {
        return std::make_tuple(first5, last3);
    } else {
        return std::make_tuple(s, "");
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("a1234år")) == (std::make_tuple("a1234", "år")));
}
