#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string old, std::string neww) {
    if (old.length() > 3) {
        return text;
    }
    if (text.find(old) != std::string::npos && text.find(' ') == std::string::npos) {
        std::string to_replace = "";
        for (int i = 0; i < old.length(); i++) {
            to_replace += neww;
        }
        size_t start_pos = text.find(old);
        if (start_pos != std::string::npos) {
            text.replace(start_pos, old.length(), to_replace);
        }
        return text;
    }
    size_t start_pos = 0;
    while ((start_pos = text.find(old, start_pos)) != std::string::npos) {
        text.replace(start_pos, old.length(), neww);
        start_pos += neww.length();
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("avacado"), ("va"), ("-")) == ("a--cado"));
}
