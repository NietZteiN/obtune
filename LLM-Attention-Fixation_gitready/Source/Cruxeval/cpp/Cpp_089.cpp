#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string charac) {
    std::string vowels = "aeiouAEIOU";
    std::string char_str(1, charac[0]);
    if (vowels.find(char_str) == std::string::npos) {
        return "None";
    }
    if (std::isupper(charac[0])) {
        return char_str;
    }
    std::transform(char_str.begin(), char_str.end(), char_str.begin(), ::toupper);
    return char_str;
}
int main() {
    auto candidate = f;
    assert(candidate(("o")) == ("O"));
}
