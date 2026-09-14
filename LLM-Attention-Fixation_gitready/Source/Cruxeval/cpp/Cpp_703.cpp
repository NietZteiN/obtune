#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string character) {
    int count = 0;
    std::string double_char = character + character;
    std::string::size_type pos = 0;
    while ((pos = text.find(double_char, pos)) != std::string::npos) {
        ++count;
        pos += double_char.size();
    }
    return text.substr(count);
}
int main() {
    auto candidate = f;
    assert(candidate(("vzzv2sg"), ("z")) == ("zzv2sg"));
}
