#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string chars) {
    int num_applies = 2;
    std::string extra_chars = "";
    for (int i = 0; i < num_applies; i++) {
        extra_chars += chars;
        size_t pos = text.find(extra_chars);
        while (pos != std::string::npos) {
            text.replace(pos, extra_chars.length(), "");
            pos = text.find(extra_chars);
        }
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("zbzquiuqnmfkx"), ("mk")) == ("zbzquiuqnmfkx"));
}
