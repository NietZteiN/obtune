#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long tab_size) {
    std::string res = "";
    text = std::regex_replace(text, std::regex("\t"), std::string(tab_size-1, ' '));
    for (int i = 0; i < text.length(); i++) {
        if (text[i] == ' ') {
            res += '|';
        }
        else {
            res += text[i];
        }
    }
    return res;
}
int main() {
    auto candidate = f;
    assert(candidate(("	a"), (3)) == ("||a"));
}
